from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ASPhaseClosureCheckReport:
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


class V112ASPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112ASPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112as_as_bounded_implementation_backfill_success",
            "v112as_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112as_waiting_state_now": True,
            "allow_row_geometry_widen_now": phase_summary.get("allow_row_geometry_widen_now"),
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112as_phase_check",
                "actual": {
                    "patch_rule_count_applied": phase_summary.get("patch_rule_count_applied"),
                    "board_backfill_coverage_ratio": phase_summary.get("board_backfill_coverage_ratio"),
                    "calendar_backfill_coverage_ratio": phase_summary.get("calendar_backfill_coverage_ratio"),
                },
                "reading": "The phase closes once the current truth rows explicitly carry the frozen implementation layer.",
            }
        ]
        interpretation = [
            "V1.12AS closes with implementation backfill complete on the current truth rows.",
            "The next lawful move is a post-patch rerun before any geometry widen.",
        ]
        return V112ASPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112as_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ASPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
