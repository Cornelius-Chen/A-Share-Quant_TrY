from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BQPhaseCheckReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BQPhaseCheckAnalyzer:
    def analyze(self, *, gate_precision_payload: dict[str, Any]) -> V112BQPhaseCheckReport:
        summary_in = dict(gate_precision_payload.get("summary", {}))
        if not bool(summary_in.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BQ phase check requires the completed gate precision sweep.")
        if int(summary_in.get("total_candidate_count", 0)) <= 0:
            raise ValueError("V1.12BQ requires at least one evaluated candidate configuration.")
        if int(summary_in.get("best_trade_count", 0)) <= 0:
            raise ValueError("V1.12BQ requires a non-cash best gate candidate.")

        summary = {
            "acceptance_posture": "keep_v112bq_as_cpo_gate_precision_sweep",
            "do_open_v112bq_now": True,
            "best_total_return": float(summary_in.get("best_total_return", 0.0)),
            "best_max_drawdown": float(summary_in.get("best_max_drawdown", 0.0)),
            "best_objective_score": float(summary_in.get("best_objective_score", 0.0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "best_gate_candidate",
                "actual": {
                    "best_candidate_signature": summary_in.get("best_candidate_signature"),
                    "neutral_drawdown_delta": summary_in.get("neutral_drawdown_delta"),
                    "best_bad_trade_suppression_rate": summary_in.get("best_bad_trade_suppression_rate"),
                },
                "reading": "The phase is only useful if it turns gate research into concrete candidate rules and suppression metrics.",
            }
        ]
        interpretation = [
            "V1.12BQ phase check confirms gate precision is now being tested as a bounded rule discovery layer rather than abstract overlay discussion.",
        ]
        return V112BQPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bq_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BQPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
