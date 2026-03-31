from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112HPhaseClosureCheckReport:
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


class V112HPhaseClosureCheckAnalyzer:
    def analyze(
        self,
        *,
        phase_check_payload: dict[str, Any],
        candidate_substate_draft_payload: dict[str, Any],
    ) -> V112HPhaseClosureCheckReport:
        phase_check_summary = dict(phase_check_payload.get("summary", {}))
        draft_summary = dict(candidate_substate_draft_payload.get("summary", {}))
        success = bool(phase_check_summary.get("ready_for_phase_closure_next")) and int(draft_summary.get("candidate_cluster_count", 0)) >= 2
        summary = {
            "acceptance_posture": "close_v112h_as_candidate_substate_draft_success" if success else "hold_v112h_open",
            "v112h_success_criteria_met": success,
            "enter_v112h_waiting_state_now": success,
            "allow_auto_label_split_now": False,
            "recommended_next_posture": "owner_review_candidate_substate_draft_before_any_formal_label_change",
        }
        evidence_rows = [
            {
                "evidence_name": "candidate_cluster_count",
                "actual": {"candidate_cluster_count": int(draft_summary.get("candidate_cluster_count", 0))},
                "reading": "The draft provides multiple candidate substates for review.",
            },
            {
                "evidence_name": "review_only_boundary",
                "actual": {"allow_auto_label_split_now": False},
                "reading": "The result remains review-only and does not authorize label rewrite.",
            },
        ]
        interpretation = [
            "This phase is successful once the candidate draft exists and remains bounded.",
            "The next lawful move is owner review, not automatic label creation.",
        ]
        return V112HPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112h_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112HPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
