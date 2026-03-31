from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112KPhaseCheckReport:
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


class V112KPhaseCheckAnalyzer:
    def analyze(self, *, draft_payload: dict[str, Any]) -> V112KPhaseCheckReport:
        draft_summary = dict(draft_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112k_as_candidate_substate_draft_success",
            "candidate_substate_count": int(draft_summary.get("candidate_substate_count", 0)),
            "formal_label_split_now": bool(draft_summary.get("formal_label_split_now")),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_candidate_substate_draft_before_any_inner_split_or_label_change",
        }
        evidence_rows = [
            {
                "evidence_name": "v112k_candidate_substate_draft",
                "actual": {
                    "candidate_substate_count": summary["candidate_substate_count"],
                    "formal_label_split_now": summary["formal_label_split_now"],
                },
                "reading": "V1.12K closes once a bounded review-only candidate-substate draft exists for high_level_consolidation.",
            }
        ]
        interpretation = [
            "V1.12K is still drafting, not legislating.",
            "The draft can guide later review, but it cannot become a formal schema by itself.",
        ]
        return V112KPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112k_phase_check_report(*, reports_dir: Path, report_name: str, result: V112KPhaseCheckReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
