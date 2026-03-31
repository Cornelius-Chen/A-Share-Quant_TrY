from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BPPhaseCheckReport:
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


class V112BPPhaseCheckAnalyzer:
    def analyze(self, *, fusion_pilot_payload: dict[str, Any]) -> V112BPPhaseCheckReport:
        summary_in = dict(fusion_pilot_payload.get("summary", {}))
        if not bool(summary_in.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BP phase check requires the completed fusion pilot.")

        summary = {
            "acceptance_posture": "keep_v112bp_as_cpo_selector_maturity_fusion_pilot",
            "do_open_v112bp_now": True,
            "trade_count": int(summary_in.get("trade_count", 0)),
            "total_return": float(summary_in.get("total_return", 0.0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "v112bp_fusion_pilot",
                "actual": {
                    "trade_count": summary_in.get("trade_count"),
                    "neutral_return_delta": summary_in.get("neutral_return_delta"),
                    "bk_drawdown_delta": summary_in.get("bk_drawdown_delta"),
                },
                "reading": "The fusion phase is only useful if it makes the selector-versus-discipline tradeoff explicit.",
            }
        ]
        interpretation = [
            "V1.12BP phase check confirms the first selector-plus-overlay fusion line exists as a bounded experiment.",
        ]
        return V112BPPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bp_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BPPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
