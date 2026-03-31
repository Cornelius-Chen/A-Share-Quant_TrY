from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AWPhaseCheckReport:
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


class V112AWPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        admission_review_payload: dict[str, Any],
    ) -> V112AWPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(admission_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112aw_as_branch_guarded_admission_review",
            "do_open_v112aw_now": charter_summary.get("do_open_v112aw_now"),
            "branch_rows_under_review": review_summary.get("branch_rows_under_review"),
            "guarded_training_context_admissible_count": review_summary.get("guarded_training_context_admissible_count"),
            "retained_review_only_count": review_summary.get("retained_review_only_count"),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": review_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "v112aw_branch_admission_review",
                "actual": {
                    "guarded_training_context_admissible_count": review_summary.get("guarded_training_context_admissible_count"),
                    "retained_review_only_count": review_summary.get("retained_review_only_count"),
                    "role_state_patch_gain": review_summary.get("role_state_patch_gain"),
                },
                "reading": "Branch admission is only valid if the project can split guarded-admissible rows from still-mixed review-only rows.",
            }
        ]
        interpretation = [
            "V1.12AW is an admissibility cut, not a promotion to formal training.",
            "Formal training and signal rights remain closed.",
        ]
        return V112AWPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112aw_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AWPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
