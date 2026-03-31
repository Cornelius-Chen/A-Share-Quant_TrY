from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112SPhaseClosureCheckReport:
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


class V112SPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112SPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112s_as_chronology_normalization_success",
            "v112s_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112s_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "recommended_next_posture": "spillover_truth_check_next",
        }
        evidence_rows = [
            {
                "evidence_name": "v112s_phase_check",
                "actual": {
                    "chronology_segment_count": phase_summary.get("chronology_segment_count"),
                    "timing_gap_count": phase_summary.get("timing_gap_count"),
                },
                "reading": "Chronology is now normalized enough that spillover truth-check can happen on a cleaner time axis.",
            }
        ]
        interpretation = [
            "V1.12S closes once flat event anchors are converted into usable chronology structure.",
            "This remains a review-layer success, not a training readiness decision.",
        ]
        return V112SPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112s_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112SPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
