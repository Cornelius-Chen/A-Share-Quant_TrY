from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112TPhaseClosureCheckReport:
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


class V112TPhaseClosureCheckAnalyzer:
    def analyze(self, *, phase_check_payload: dict[str, Any]) -> V112TPhaseClosureCheckReport:
        phase_summary = dict(phase_check_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "close_v112t_as_spillover_truth_check_success",
            "v112t_success_criteria_met": bool(phase_summary.get("ready_for_phase_closure_next")),
            "enter_v112t_waiting_state_now": True,
            "allow_auto_training_now": False,
            "allow_auto_feature_promotion_now": False,
            "recommended_next_posture": "owner_review_of_cpo_foundation_completeness_and_research_readiness",
        }
        evidence_rows = [
            {
                "evidence_name": "v112t_phase_check",
                "actual": {
                    "candidate_a_share_spillover_factor_count": phase_summary.get("candidate_a_share_spillover_factor_count"),
                    "pure_name_bonus_or_board_follow_count": phase_summary.get("pure_name_bonus_or_board_follow_count"),
                },
                "reading": "Spillover rows are now separated into reviewable categories without forcing premature deletion or promotion.",
            }
        ]
        interpretation = [
            "V1.12T closes once the spillover bucket is classified rather than left as flat noise.",
            "The next correct move is an owner-level review of overall CPO information-foundation completeness, not automatic training.",
        ]
        return V112TPhaseClosureCheckReport(summary=summary, evidence_rows=evidence_rows, interpretation=interpretation)


def write_v112t_phase_closure_check_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112TPhaseClosureCheckReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
