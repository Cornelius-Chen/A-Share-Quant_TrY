from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AQPhaseClosureCheckReport:
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


class V112AQPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112AQPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112aq_as_bounded_feature_implementation_patch_review_success",
            "v112aq_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112aq_waiting_state_now": True,
            "allow_row_geometry_widen_now": phase_summary.get("allow_row_geometry_widen_now"),
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "recommended_next_posture": phase_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112aq_phase_check",
                "actual": {
                    "should_patch_feature_implementation_before_row_widen": phase_summary.get(
                        "should_patch_feature_implementation_before_row_widen"
                    ),
                    "minimum_patch_rule_count": phase_summary.get("minimum_patch_rule_count"),
                },
                "reading": "The review closes once the next lawful move is narrowed to a concrete patch set.",
            }
        ]
        interpretation = [
            "V1.12AQ closes with a bounded implementation decision, not with a widened experiment.",
            "Formal training and signal rights remain closed.",
        ]
        return V112AQPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112aq_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AQPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
