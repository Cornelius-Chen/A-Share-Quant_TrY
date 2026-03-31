from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112UPhaseCheckReport:
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


class V112UPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        readiness_review_payload: dict[str, Any],
    ) -> V112UPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        review_summary = dict(readiness_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112u_as_owner_level_readiness_review_only",
            "do_open_v112u_now": charter_summary.get("do_open_v112u_now"),
            "foundation_is_normed_for_research": review_summary.get("foundation_is_normed_for_research"),
            "foundation_is_complete_enough_for_bounded_research": review_summary.get("foundation_is_complete_enough_for_bounded_research"),
            "foundation_is_complete_enough_for_formal_training": review_summary.get("foundation_is_complete_enough_for_formal_training"),
            "remaining_material_gap_count": review_summary.get("remaining_material_gap_count"),
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": review_summary.get("recommended_next_posture"),
        }
        evidence_rows = [
            {
                "evidence_name": "cpo_foundation_readiness_review",
                "actual": {
                    "foundation_is_normed_for_research": review_summary.get("foundation_is_normed_for_research"),
                    "foundation_is_complete_enough_for_bounded_research": review_summary.get("foundation_is_complete_enough_for_bounded_research"),
                    "foundation_is_complete_enough_for_formal_training": review_summary.get("foundation_is_complete_enough_for_formal_training"),
                    "remaining_material_gap_count": review_summary.get("remaining_material_gap_count"),
                },
                "reading": "The foundation is good enough for bounded research but still below the threshold for formal training.",
            }
        ]
        interpretation = [
            "V1.12U is a readiness judgment, not an implementation phase.",
            "Its output narrows the next decision to owner-level research posture selection.",
        ]
        return V112UPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112u_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112UPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
