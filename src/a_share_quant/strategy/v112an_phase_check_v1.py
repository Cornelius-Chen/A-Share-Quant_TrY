from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ANPhaseCheckReport:
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


class V112ANPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        result_review_payload: dict[str, Any],
    ) -> V112ANPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(result_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112an_as_core_skeleton_pilot_result_review",
            "do_open_v112an_now": charter_summary.get("do_open_v112an_now"),
            "best_family_for_phase": review_summary.get("best_family_for_phase"),
            "best_family_for_catalyst_sequence": review_summary.get("best_family_for_catalyst_sequence"),
            "best_family_for_role_state": review_summary.get("best_family_for_role_state"),
            "role_confusion_count": review_summary.get("role_confusion_count"),
            "correction_bucket_count": review_summary.get("correction_bucket_count"),
            "allow_auto_training_now": False,
            "allow_auto_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": review_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112an_result_review",
                "actual": {
                    "best_family_for_phase": review_summary.get("best_family_for_phase"),
                    "best_family_for_role_state": review_summary.get("best_family_for_role_state"),
                    "correction_bucket_count": review_summary.get("correction_bucket_count"),
                },
                "reading": "The project now knows what the tiny pilot learned most easily and where the residual difficulty concentrates.",
            }
        ]
        interpretation = [
            "V1.12AN succeeds if pilot behavior becomes explainable rather than merely measurable.",
            "Training still remains closed after the review.",
        ]
        return V112ANPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112an_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ANPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
