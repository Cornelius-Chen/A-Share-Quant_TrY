from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BUPhaseCheckReport:
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


class V112BUPhaseCheckAnalyzer:
    def analyze(self, *, control_pilot_payload: dict[str, Any]) -> V112BUPhaseCheckReport:
        summary_in = dict(control_pilot_payload.get("summary", {}))
        if not bool(summary_in.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BU phase check requires the completed control pilot report.")

        summary = {
            "acceptance_posture": "keep_v112bu_as_phase_conditioned_control_pilot",
            "trade_count": int(summary_in.get("trade_count", 0)),
            "vetoed_trade_count": int(summary_in.get("vetoed_trade_count", 0)),
            "holding_veto_half_life_count": int(summary_in.get("holding_veto_half_life_count", 0)),
            "ready_for_phase_closure_next": True,
        }
        evidence_rows = [
            {
                "evidence_name": "phase_conditioned_control_application",
                "actual": {
                    "trade_count": summary_in.get("trade_count"),
                    "vetoed_trade_count": summary_in.get("vetoed_trade_count"),
                    "holding_veto_half_life_count": summary_in.get("holding_veto_half_life_count"),
                    "bp_drawdown_delta": summary_in.get("bp_drawdown_delta"),
                    "bp_return_delta": summary_in.get("bp_return_delta"),
                },
                "reading": "The control pilot matters only if it actually changes the trade path and can be compared against the frozen fusion baseline.",
            }
        ]
        interpretation = [
            "V1.12BU phase check confirms that explicit control objects have now been exercised on a lawful baseline instead of staying as abstract extracted rules.",
        ]
        return V112BUPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112bu_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BUPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
