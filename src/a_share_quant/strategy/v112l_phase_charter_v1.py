from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112LPhaseCharterReport:
    summary: dict[str, Any]
    mission: dict[str, Any]
    in_scope: list[str]
    out_of_scope: list[str]
    success_criteria: list[str]
    stop_criteria: list[str]
    handoff_condition: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "mission": self.mission,
            "in_scope": self.in_scope,
            "out_of_scope": self.out_of_scope,
            "success_criteria": self.success_criteria,
            "stop_criteria": self.stop_criteria,
            "handoff_condition": self.handoff_condition,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112LPhaseCharterAnalyzer:
    def analyze(self, *, prior_phase_payload: dict[str, Any]) -> V112LPhaseCharterReport:
        prior_summary = dict(prior_phase_payload.get("summary", {}))
        recommended_next_posture = str(prior_summary.get("recommended_next_posture", ""))
        if recommended_next_posture != "preserve_v112k_as_review_only_candidate_draft_until_owner_decides_on_any_inner_split_follow_up":
            raise ValueError("V1.12L requires the V1.12K closure posture to preserve the review-only draft.")

        summary = {
            "acceptance_posture": "open_v112l_candidate_substate_owner_review",
            "phase_name": "V1.12L Candidate Substate Owner Review",
            "ready_for_owner_review_next": True,
        }
        mission = {
            "goal": (
                "Review the V1.12K candidate-substate draft and decide which pieces are worth preserving as review-only "
                "candidate substates versus keeping only as future inner-drafting targets."
            ),
            "why_now": (
                "V1.12K already produced a bounded review-only draft, so the next lawful move is preservation review "
                "rather than immediate inner splitting or formal relabeling."
            ),
        }
        in_scope = [
            "review-only preserve/reject judgment on the three V1.12K candidate substate rows",
            "separating preservable review-only candidate substates from mixed drafting-only structures",
            "keeping high_level_consolidation as the only stage under review",
        ]
        out_of_scope = [
            "formal label split",
            "inner drafting execution",
            "major_markup follow-up",
            "dataset widening",
            "model escalation",
        ]
        success_criteria = [
            "a bounded preserve/reject decision exists for each V1.12K candidate substate row",
            "at least one preserved review-only candidate substate remains usable without formal label action",
            "mixed structures remain explicitly blocked from automatic promotion into formal schema",
        ]
        stop_criteria = [
            "the review collapses into de facto label legislation",
            "the review requires widening scope beyond the existing V1.12K draft before any judgment is possible",
        ]
        handoff_condition = (
            "mainline can decide whether to stop at preserved review-only substates or open one further bounded "
            "inner-drafting pass only for the mixed stall cluster"
        )
        return V112LPhaseCharterReport(
            summary=summary,
            mission=mission,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            success_criteria=success_criteria,
            stop_criteria=stop_criteria,
            handoff_condition=handoff_condition,
        )


def write_v112l_phase_charter_report(
    *, reports_dir: Path, report_name: str, result: V112LPhaseCharterReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
