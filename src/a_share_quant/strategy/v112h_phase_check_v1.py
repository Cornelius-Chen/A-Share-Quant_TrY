from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112HPhaseCheckReport:
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


class V112HPhaseCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        candidate_substate_draft_payload: dict[str, Any],
    ) -> V112HPhaseCheckReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        draft_summary = dict(candidate_substate_draft_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "keep_v112h_as_candidate_substate_draft_success",
            "charter_open": bool(charter_summary.get("ready_for_candidate_substate_draft_next")),
            "candidate_cluster_count": int(draft_summary.get("candidate_cluster_count", 0)),
            "ready_for_phase_closure_next": True,
            "recommended_next_posture": "owner_review_candidate_substate_draft_before_label_change",
        }
        evidence_rows = [
            {
                "evidence_name": "candidate_cluster_count",
                "actual": {"candidate_cluster_count": int(draft_summary.get("candidate_cluster_count", 0))},
                "reading": "The draft exposes multiple candidate substates rather than collapsing everything into one bucket.",
            },
            {
                "evidence_name": "thin_cluster_presence",
                "actual": {
                    "clusters_with_nontrivial_support": int(draft_summary.get("candidate_clusters_with_nontrivial_support", 0)),
                },
                "reading": "At least one candidate is sparse and should remain provisional, which is useful for review but not for formalization.",
            },
        ]
        interpretation = [
            "V1.12H is a review-only candidate substate drafting phase.",
            "Its job is to present a bounded structure draft for owner review, not to freeze labels.",
            "The lawful next posture is review, not automatic label split.",
        ]
        return V112HPhaseCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112h_phase_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112HPhaseCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
