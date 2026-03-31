from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112LPhaseCheckReport:
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


class V112LPhaseCheckAnalyzer:
    def analyze(self, *, owner_review_payload: dict[str, Any]) -> V112LPhaseCheckReport:
        review_summary = dict(owner_review_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112l_as_review_only_preservation_success",
            "preserved_review_only_count": int(review_summary.get("preserved_review_only_count", 0)),
            "mixed_inner_drafting_target_count": int(review_summary.get("mixed_inner_drafting_target_count", 0)),
            "formal_label_split_now": bool(review_summary.get("formal_label_split_now")),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "preserve_review_only_substates_and_pause_before_any_optional_inner_drafting",
        }
        evidence_rows = [
            {
                "evidence_name": "v112l_candidate_substate_owner_review",
                "actual": {
                    "preserved_review_only_count": summary["preserved_review_only_count"],
                    "mixed_inner_drafting_target_count": summary["mixed_inner_drafting_target_count"],
                    "formal_label_split_now": summary["formal_label_split_now"],
                },
                "reading": (
                    "V1.12L succeeds once the V1.12K draft is reduced to preserved review-only substates plus any "
                    "remaining mixed drafting target."
                ),
            }
        ]
        interpretation = [
            "V1.12L keeps only the review-only pieces worth preserving.",
            "It still does not authorize a formal label split or automatic inner-drafting continuation.",
        ]
        return V112LPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112l_phase_check_report(*, reports_dir: Path, report_name: str, result: V112LPhaseCheckReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
