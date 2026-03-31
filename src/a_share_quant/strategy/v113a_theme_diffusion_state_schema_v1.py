from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V113AThemeDiffusionStateSchemaReport:
    summary: dict[str, Any]
    phase_state_rows: list[dict[str, Any]]
    stock_role_rows: list[dict[str, Any]]
    strength_dimension_rows: list[dict[str, Any]]
    driver_dimension_rows: list[dict[str, Any]]
    open_candidate_layer_rows: list[dict[str, Any]]
    review_only_candidate_driver_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "phase_state_rows": self.phase_state_rows,
            "stock_role_rows": self.stock_role_rows,
            "strength_dimension_rows": self.strength_dimension_rows,
            "driver_dimension_rows": self.driver_dimension_rows,
            "open_candidate_layer_rows": self.open_candidate_layer_rows,
            "review_only_candidate_driver_rows": self.review_only_candidate_driver_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V113AThemeDiffusionStateSchemaAnalyzer:
    def analyze(self, *, phase_charter_payload: dict[str, Any]) -> V113AThemeDiffusionStateSchemaReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_schema_freeze_next")):
            raise ValueError("V1.13A requires an open schema charter.")

        phase_state_rows = [
            {
                "state_name": "ignition",
                "state_reading": "The theme first breaks into market attention and starts to detach from background noise.",
                "minimum_observables": [
                    "leader_strength_present",
                    "initial_breadth_activation_present",
                    "context_driver_activation_present",
                ],
            },
            {
                "state_name": "diffusion",
                "state_reading": "The theme expands from core names into a broader cohort with catch-up and confirmation behavior.",
                "minimum_observables": [
                    "breadth_expansion_present",
                    "mid_core_confirmation_present",
                    "laggard_activation_present",
                ],
            },
            {
                "state_name": "relay",
                "state_reading": "The theme survives through role handoff rather than only first-leader continuation.",
                "minimum_observables": [
                    "relay_success_present",
                    "leader_continuation_or_transfer_present",
                    "absorption_quality_not_broken",
                ],
            },
            {
                "state_name": "decay",
                "state_reading": "The theme loses breadth, handoff quality, or absorption and starts to become vulnerable to A-kill behavior.",
                "minimum_observables": [
                    "breadth_contraction_present",
                    "relay_failure_present",
                    "a_kill_risk_elevated",
                ],
            },
        ]
        stock_role_rows = [
            {
                "role_name": "leader",
                "role_reading": "The name carrying height and direction-setting responsibility for the theme.",
            },
            {
                "role_name": "mid_core",
                "role_reading": "The stabilizing core or mid-cap confirmation name that helps the theme survive beyond a single spearhead.",
            },
            {
                "role_name": "laggard_catchup",
                "role_reading": "The delayed beneficiary or lower-positioned name activated during diffusion or late expansion.",
            },
            {
                "role_name": "mapping_activation",
                "role_reading": "The weaker or indirect mapping name activated by narrative spillover rather than direct leadership.",
            },
        ]
        strength_dimension_rows = [
            {
                "dimension_name": "mainline_persistence_level",
                "reading": "How long and how repeatedly the mainline can keep strengthening across days or weeks.",
            },
            {
                "dimension_name": "mainline_height_level",
                "reading": "How far the theme has built vertical depth through leader height, mid-core follow-through, and laggard spread.",
            },
            {
                "dimension_name": "mainline_absorption_quality",
                "reading": "How well the theme absorbs supply during pullbacks or high-level consolidation instead of collapsing into A-kill.",
            },
            {
                "dimension_name": "a_kill_risk_level",
                "reading": "How vulnerable the theme currently is to fast post-peak collapse or failed relay behavior.",
            },
        ]
        driver_dimension_rows = [
            {
                "driver_name": "policy_backing_tier",
                "reading": "Whether the theme is backed by national strategy, industry encouragement, or only weak narrative support.",
                "source_kind": "context_driver",
            },
            {
                "driver_name": "industrial_advantage_alignment",
                "reading": "Whether the theme aligns with a real domestic industrial advantage or only a loose story shell.",
                "source_kind": "context_driver",
            },
            {
                "driver_name": "market_regime_tailwind",
                "reading": "Whether the broader tape, risk appetite, and index environment amplify the theme instead of fighting it.",
                "source_kind": "context_driver",
            },
            {
                "driver_name": "event_resonance_intensity",
                "reading": "Whether multiple policy, industry, overseas, or narrative events are resonating at the same time.",
                "source_kind": "context_driver",
            },
        ]
        open_candidate_layer_rows = [
            {
                "candidate_slot_name": "candidate_policy_or_regulatory_driver",
                "current_posture": "open_for_review_only_discovery",
                "reading": "Reserved for later discovery of more specific policy-strength proxies.",
            },
            {
                "candidate_slot_name": "candidate_market_environment_driver",
                "current_posture": "open_for_review_only_discovery",
                "reading": "Reserved for later discovery of tape/regime variables such as trend persistence or broad risk-on context.",
            },
            {
                "candidate_slot_name": "candidate_event_resonance_driver",
                "current_posture": "open_for_review_only_discovery",
                "reading": "Reserved for later discovery of repeatable multi-event resonance patterns.",
            },
            {
                "candidate_slot_name": "candidate_role_spread_driver",
                "current_posture": "open_for_review_only_discovery",
                "reading": "Reserved for later discovery of role-spread or catch-up intensity variables.",
            },
        ]
        review_only_candidate_driver_rows = [
            {
                "candidate_driver_name": "policy_backing_tier",
                "candidate_priority_tier": "high",
                "candidate_bucket": "policy_or_industry",
                "reading": "National-strategy or regulator-level backing appears repeatedly in stronger mainlines.",
            },
            {
                "candidate_driver_name": "industrial_advantage_alignment",
                "candidate_priority_tier": "high",
                "candidate_bucket": "policy_or_industry",
                "reading": "Real domestic industrial advantage repeatedly appears in more durable theme diffusion lines.",
            },
            {
                "candidate_driver_name": "market_regime_tailwind",
                "candidate_priority_tier": "high",
                "candidate_bucket": "market_environment",
                "reading": "Broad tape support and risk appetite act as recurring amplifiers rather than isolated noise.",
            },
            {
                "candidate_driver_name": "event_resonance_intensity",
                "candidate_priority_tier": "high",
                "candidate_bucket": "event_resonance",
                "reading": "Multiple overlapping events often separate large mainlines from one-shot theme spikes.",
            },
            {
                "candidate_driver_name": "leader_height_establishment",
                "candidate_priority_tier": "medium",
                "candidate_bucket": "market_environment",
                "reading": "A theme usually needs visible leader height before it becomes a real mainline.",
            },
            {
                "candidate_driver_name": "mid_core_confirmation",
                "candidate_priority_tier": "medium",
                "candidate_bucket": "market_environment",
                "reading": "Stronger lines usually gain mid-core confirmation rather than staying single-core only.",
            },
            {
                "candidate_driver_name": "cross_day_breadth_diffusion",
                "candidate_priority_tier": "medium",
                "candidate_bucket": "market_environment",
                "reading": "Cross-day breadth expansion appears more meaningful than one-day broad spikes.",
            },
            {
                "candidate_driver_name": "absorption_quality_or_a_kill_suppression",
                "candidate_priority_tier": "medium",
                "candidate_bucket": "market_environment",
                "reading": "Strong lines repeatedly show better absorption and less A-kill vulnerability.",
            },
            {
                "candidate_driver_name": "catalyst_freshness_and_reinforcement",
                "candidate_priority_tier": "medium",
                "candidate_bucket": "event_resonance",
                "reading": "Fresh catalysts and repeated reinforcement often matter more than already-exhausted narratives.",
            },
            {
                "candidate_driver_name": "mapping_clarity_and_tradeable_story",
                "candidate_priority_tier": "deferred",
                "candidate_bucket": "borderline_candidate",
                "reading": "Worth preserving in review, but still too noisy to freeze as a formal driver.",
            },
        ]
        summary = {
            "acceptance_posture": "freeze_v113a_theme_diffusion_state_schema_v1",
            "phase_state_count": len(phase_state_rows),
            "stock_role_count": len(stock_role_rows),
            "strength_dimension_count": len(strength_dimension_rows),
            "driver_dimension_count": len(driver_dimension_rows),
            "open_candidate_slot_count": len(open_candidate_layer_rows),
            "review_only_candidate_driver_count": len(review_only_candidate_driver_rows),
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.13A freezes a bounded grammar for theme-diffusion carry before any model or execution work begins.",
            "The schema explicitly separates state, role, strength, and context-backed drivers instead of collapsing them into one bucket.",
            "The open candidate layer records that more drivers may exist, but keeps them unfrozen until later review.",
            "Cross-case driver candidates are preserved as review-only candidate drivers rather than formal schema law.",
        ]
        return V113AThemeDiffusionStateSchemaReport(
            summary=summary,
            phase_state_rows=phase_state_rows,
            stock_role_rows=stock_role_rows,
            strength_dimension_rows=strength_dimension_rows,
            driver_dimension_rows=driver_dimension_rows,
            open_candidate_layer_rows=open_candidate_layer_rows,
            review_only_candidate_driver_rows=review_only_candidate_driver_rows,
            interpretation=interpretation,
        )


def write_v113a_theme_diffusion_state_schema_report(
    *, reports_dir: Path, report_name: str, result: V113AThemeDiffusionStateSchemaReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
