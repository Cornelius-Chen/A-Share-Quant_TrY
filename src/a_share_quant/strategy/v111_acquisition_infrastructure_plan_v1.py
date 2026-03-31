from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V111AcquisitionInfrastructurePlanReport:
    summary: dict[str, Any]
    plan: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "plan": self.plan,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V111AcquisitionInfrastructurePlanAnalyzer:
    """Freeze sustained catalyst evidence acquisition infrastructure."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
    ) -> V111AcquisitionInfrastructurePlanReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v111_now")):
            raise ValueError("V1.11 must be open before the acquisition infrastructure plan can be frozen.")

        plan = {
            "acquisition_scope": [
                "national_or_ministry_level policy continuation",
                "industry-level multi-day reinforcement catalysts",
                "project, order, or capacity-expansion catalysts with board-level followthrough",
                "cross-symbol-family followthrough candidates beyond existing anchor families",
            ],
            "source_hierarchy": [
                "tier_1_official_policy_and_regulatory_sources",
                "tier_2_company_and_supply_chain_announcements",
                "tier_3_industry_conference_or_project_landing_sources",
                "tier_4_market_confirmation_layer_for_board_breadth_and_turnover_followthrough",
            ],
            "admissibility_rules": [
                "candidate must be point_in_time_recordable",
                "candidate must have source_tier and source_ref",
                "candidate must have market_confirmation evidence",
                "candidate must not be single-day pulse only",
                "candidate must be admissible under frozen bounded collection rules before entering any later probe",
            ],
            "family_novelty_rules": [
                "new_symbol_family must differ from existing anchor family by symbol cluster",
                "same_story_different_shell is not sufficient novelty",
                "same_symbol same_event_day clusters are automatically non-novel",
                "family novelty requires both symbol separation and at least one context distinction",
            ],
            "point_in_time_recording_rules": [
                "record event_date, window_start, window_end",
                "record primary_source_ref and source_authority_tier",
                "record policy_scope or industry_scope",
                "record board-level confirmation and followthrough days",
                "record candidate link into concept/catalyst registry before any later evidence review",
            ],
            "refresh_cadence": [
                "weekly source sweep for high-priority official and announcement layers",
                "event-driven trigger intake when a new board-level followthrough theme appears",
                "bounded monthly novelty audit to prevent same-story shell recycling",
            ],
            "bounded_first_pilot_plan": {
                "pilot_goal": "collect the first truly new cross-family policy-followthrough candidate pool",
                "pilot_candidate_cap": 5,
                "pilot_admission_cap": 2,
                "pilot_priority_order": [
                    "official_policy_or_regulatory_followthrough",
                    "industry_reinforcement_with_board_confirmation",
                    "project_or_order_followthrough_with_multi-day breadth",
                ],
            },
            "feature_shadow_constraints": [
                "each newly acquired candidate must state which existing provisional feature it supports or challenges",
                "each candidate must record whether it increases observable breadth or just duplicates an existing story shape",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v111_acquisition_infrastructure_plan_v1",
            "acquisition_scope_count": len(plan["acquisition_scope"]),
            "source_hierarchy_count": len(plan["source_hierarchy"]),
            "admissibility_rule_count": len(plan["admissibility_rules"]),
            "family_novelty_rule_count": len(plan["family_novelty_rules"]),
            "ready_for_bounded_first_pilot_next": True,
        }
        interpretation = [
            "V1.11 defines how future evidence should be acquired repeatedly, not how to patch the current pool once.",
            "The plan forces novelty, point-in-time recording, and source-aware confirmation before any later probe or promotion review.",
            "The next legal step is a bounded first pilot built on this protocol, not direct case scavenging or strategy integration.",
        ]
        return V111AcquisitionInfrastructurePlanReport(summary=summary, plan=plan, interpretation=interpretation)


def write_v111_acquisition_infrastructure_plan_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V111AcquisitionInfrastructurePlanReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
