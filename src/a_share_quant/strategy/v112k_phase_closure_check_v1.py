from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112KPhaseClosureCheckReport:
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


class V112KPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112KPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112k_as_candidate_substate_draft_success",
            "v112k_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112k_waiting_state_now": True,
            "allow_auto_label_split_now": False,
            "recommended_next_posture": "preserve_v112k_as_review_only_candidate_draft_until_owner_decides_on_any_inner_split_follow_up",
        }
        evidence_rows = [
            {
                "evidence_name": "v112k_phase_check",
                "actual": {
                    "candidate_substate_count": phase_summary.get("candidate_substate_count"),
                    "formal_label_split_now": phase_summary.get("formal_label_split_now"),
                },
                "reading": "V1.12K closes once the bounded candidate-substate draft exists and remains review-only.",
            }
        ]
        interpretation = [
            "V1.12K does not authorize a formal label split.",
            "It only preserves a small candidate-substate draft for later owner judgment.",
        ]
        return V112KPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112k_phase_closure_check_report(
    *, reports_dir: Path, report_name: str, result: V112KPhaseClosureCheckReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
