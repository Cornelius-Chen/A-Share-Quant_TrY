from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112VPhaseClosureCheckReport:
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


class V112VPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112VPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112v_as_board_chronology_operationalization_success",
            "v112v_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112v_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112v_phase_check",
                "actual": {
                    "daily_series_count": phase_summary.get("daily_series_count"),
                    "table_column_count": phase_summary.get("table_column_count"),
                    "remaining_operational_gap_count": phase_summary.get("remaining_operational_gap_count"),
                },
                "reading": "The board chronology series gap is now operationalized enough to be reviewable and auditable.",
            }
        ]
        interpretation = [
            "V1.12V closes once the daily board chronology series has a bounded operational spec.",
            "The next move still depends on owner-level prioritization of the remaining material gaps.",
        ]
        return V112VPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112v_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112VPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
