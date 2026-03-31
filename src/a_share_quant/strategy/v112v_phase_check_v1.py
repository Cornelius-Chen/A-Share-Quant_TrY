from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112VPhaseCheckReport:
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


class V112VPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        operationalization_payload: dict[str, Any],
    ) -> V112VPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        operational_summary = dict(operationalization_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112v_as_board_chronology_operationalization_only",
            "do_open_v112v_now": charter_summary.get("do_open_v112v_now"),
            "daily_series_count": operational_summary.get("daily_series_count"),
            "table_column_count": operational_summary.get("table_column_count"),
            "source_precedence_count": operational_summary.get("source_precedence_count"),
            "remaining_operational_gap_count": operational_summary.get("remaining_operational_gap_count"),
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "continue_material_gap_reduction_or_owner_review",
        }
        evidence_rows = [
            {
                "evidence_name": "daily_board_chronology_operationalization",
                "actual": {
                    "daily_series_count": operational_summary.get("daily_series_count"),
                    "table_column_count": operational_summary.get("table_column_count"),
                    "remaining_operational_gap_count": operational_summary.get("remaining_operational_gap_count"),
                },
                "reading": "The board chronology gap now has a bounded operational target rather than only an abstract description.",
            }
        ]
        interpretation = [
            "V1.12V remains an information-foundation operationalization pass.",
            "It reduces one material gap without opening training.",
        ]
        return V112VPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112v_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112VPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
