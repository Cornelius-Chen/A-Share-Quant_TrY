from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112KPhaseCharterReport:
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


class V112KPhaseCharterAnalyzer:
    def analyze(self, *, prior_phase_payload: dict[str, Any]) -> V112KPhaseCharterReport:
        prior_summary = dict(prior_phase_payload.get("summary", {}))
        follow_up_stage = str(prior_summary.get("bounded_follow_up_stage", ""))
        if not follow_up_stage:
            for row in prior_phase_payload.get("evidence_rows", []):
                actual = row.get("actual", {})
                if isinstance(actual, dict) and str(actual.get("bounded_follow_up_stage", "")):
                    follow_up_stage = str(actual.get("bounded_follow_up_stage"))
                    break
        if follow_up_stage != "high_level_consolidation":
            raise ValueError("V1.12K requires V1.12J to narrow bounded follow-up to high_level_consolidation.")

        summary = {
            "acceptance_posture": "open_v112k_high_level_consolidation_candidate_substate_drafting",
            "phase_name": "V1.12K High-Level Consolidation Candidate Substate Drafting",
            "ready_for_drafting_next": True,
        }
        mission = {
            "goal": (
                "Turn the high_level_consolidation candidate buckets into a small review-only candidate-substate draft "
                "without freezing any formal label changes."
            ),
            "why_now": (
                "V1.12J concluded that only high_level_consolidation deserves bounded drafting follow-up."
            ),
        }
        in_scope = [
            "review-only candidate substates for high_level_consolidation",
            "mapping from bucket structure to candidate draft names and meanings",
            "readiness judgment for which draft pieces are usable now versus still mixed",
        ]
        out_of_scope = [
            "formal label split",
            "major_markup follow-up",
            "dataset widening",
            "model escalation",
            "strategy integration",
        ]
        success_criteria = [
            "a small candidate-substate draft exists for high_level_consolidation",
            "the draft distinguishes strong candidates from mixed or too-thin buckets",
            "the output remains review-only and does not legislate new formal labels",
        ]
        stop_criteria = [
            "drafting collapses into a formal relabeling attempt",
            "drafting requires scope growth before any useful draft can be written",
        ]
        handoff_condition = "owner can review the candidate draft and decide whether any bounded draft should be refined further"
        return V112KPhaseCharterReport(
            summary=summary,
            mission=mission,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            success_criteria=success_criteria,
            stop_criteria=stop_criteria,
            handoff_condition=handoff_condition,
        )


def write_v112k_phase_charter_report(
    *, reports_dir: Path, report_name: str, result: V112KPhaseCharterReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
