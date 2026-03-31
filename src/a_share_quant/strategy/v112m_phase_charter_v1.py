from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112MPhaseCharterReport:
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


class V112MPhaseCharterAnalyzer:
    def analyze(self, *, prior_phase_payload: dict[str, Any]) -> V112MPhaseCharterReport:
        prior_summary = dict(prior_phase_payload.get("summary", {}))
        recommended_next_posture = str(prior_summary.get("recommended_next_posture", ""))
        if recommended_next_posture != "keep_two_review_only_substates_and_one_mixed_target_frozen_until_explicit_owner_decision":
            raise ValueError("V1.12M requires V1.12L to preserve the mixed target for explicit reopen only.")

        summary = {
            "acceptance_posture": "open_v112m_mixed_high_level_stall_inner_drafting",
            "phase_name": "V1.12M Mixed High-Level Stall Inner Drafting",
            "ready_for_inner_draft_next": True,
        }
        mission = {
            "goal": (
                "Run one bounded inner-drafting pass only inside the mixed high-level stall cluster to see whether a "
                "small number of review-only inner structures can be separated without formal label action."
            ),
            "why_now": (
                "V1.12L preserved the mixed stall cluster only as an optional future target, and the owner explicitly "
                "reopened exactly that target."
            ),
        }
        in_scope = [
            "only the mixed high-level stall cluster from V1.12L",
            "review-only inner draft based on existing frozen pilot data and existing semantic-v2 features",
            "small number of candidate inner structures plus any unresolved residue",
        ]
        out_of_scope = [
            "formal label split",
            "high_level_consolidation buckets outside the mixed stall cluster",
            "major_markup follow-up",
            "dataset widening",
            "model escalation",
        ]
        success_criteria = [
            "the mixed stall cluster is reduced into a small review-only inner draft",
            "at least one inner draft has nontrivial support and distinct reading",
            "any unresolved residue remains explicit instead of being forced into a fake clean split",
        ]
        stop_criteria = [
            "the inner draft requires changing the formal label system",
            "the mixed stall cluster cannot be separated into anything more useful than noise",
        ]
        handoff_condition = (
            "mainline can decide whether the inner draft adds enough review value to preserve, or whether the mixed "
            "stall cluster should remain frozen as unresolved"
        )
        return V112MPhaseCharterReport(
            summary=summary,
            mission=mission,
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            success_criteria=success_criteria,
            stop_criteria=stop_criteria,
            handoff_condition=handoff_condition,
        )


def write_v112m_phase_charter_report(
    *, reports_dir: Path, report_name: str, result: V112MPhaseCharterReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
