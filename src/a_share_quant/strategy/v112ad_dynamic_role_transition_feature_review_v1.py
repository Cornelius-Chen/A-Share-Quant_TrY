from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112ADDynamicRoleTransitionFeatureReviewReport:
    summary: dict[str, Any]
    transition_event_rows: list[dict[str, Any]]
    dynamic_feature_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "transition_event_rows": self.transition_event_rows,
            "dynamic_feature_rows": self.dynamic_feature_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112ADDynamicRoleTransitionFeatureReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        reconstruction_payload: dict[str, Any],
        cohort_map_payload: dict[str, Any],
        unsupervised_probe_payload: dict[str, Any],
    ) -> V112ADDynamicRoleTransitionFeatureReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112ad_now")):
            raise ValueError("V1.12AD must be open before dynamic role-transition review runs.")

        transition_event_rows = [
            {
                "event_name": "ignition_to_main_markup_leader_lock_in",
                "from_stage": "ignition_1",
                "to_stage": "main_markup_1",
                "dominant_symbols": ["300308", "300502"],
                "role_reading": "leadership stops being only a breakout event and becomes persistent markup leadership",
                "candidate_features": ["role_persistence_score", "leader_retention_state"],
            },
            {
                "event_name": "core_markup_to_diffusion_challenger_activation",
                "from_stage": "main_markup_1",
                "to_stage": "diffusion_1",
                "dominant_symbols": ["002281", "603083", "688205", "301205", "300570"],
                "role_reading": "non-core objects are not equal; some become valid challengers while others remain branch-only",
                "candidate_features": ["challenger_activation_state", "breadth_confirmed_role_upgrade_flag"],
            },
            {
                "event_name": "diffusion_to_divergence_quality_split",
                "from_stage": "diffusion_1",
                "to_stage": "divergence_decay_1",
                "dominant_symbols": ["300308", "300502", "603083", "688205"],
                "role_reading": "the market starts separating durable leaders from weaker diffusion beneficiaries",
                "candidate_features": ["role_demotion_risk_state", "legacy_leader_absorption_state"],
            },
            {
                "event_name": "quiet_reset_to_reignition_route_depth_upgrade",
                "from_stage": "deep_reset_quiet_window",
                "to_stage": "re_ignition_markup_2",
                "dominant_symbols": ["688498", "688313", "300757"],
                "role_reading": "branch and implementation rows can upgrade in relevance when route depth becomes market-salient",
                "candidate_features": ["branch_upgrade_state", "route_depth_upgrade_flag"],
            },
            {
                "event_name": "reignition_to_major_markup_beta_requalification",
                "from_stage": "re_ignition_markup_2",
                "to_stage": "major_markup_3",
                "dominant_symbols": ["300308", "300502", "300394", "603083", "688205", "301205"],
                "role_reading": "core and challenger beta can both re-qualify when the narrative becomes cleaner and board resonance improves",
                "candidate_features": ["role_requalification_state", "mainline_breadth_reacceptance_flag"],
            },
            {
                "event_name": "major_markup_to_laggard_catchup_spillover_saturation",
                "from_stage": "major_markup_3",
                "to_stage": "laggard_catchup_3",
                "dominant_symbols": ["601869", "600487", "600522", "000070", "603228"],
                "role_reading": "late extension and spillover gain stage information value while losing business-purity value",
                "candidate_features": ["spillover_saturation_state", "late_extension_maturity_flag"],
            },
            {
                "event_name": "laggard_catchup_to_final_decay_residual_core_vs_collapse",
                "from_stage": "laggard_catchup_3",
                "to_stage": "divergence_decay_3",
                "dominant_symbols": ["300308", "300394", "000070", "603228", "001267"],
                "role_reading": "some rows retain residual core strength while late spillover collapses or fades into memory",
                "candidate_features": ["residual_core_strength_state", "spillover_collapse_risk_state"],
            },
        ]

        dynamic_feature_rows = [
            {
                "feature_name": "role_persistence_score",
                "feature_family": "dynamic_role_core",
                "reading": "Measures whether an object keeps its role across adjacent stages instead of only flashing once.",
                "best_used_for": "leader stability and mid-cycle quality control",
                "status": "review_only_dynamic_feature_candidate",
            },
            {
                "feature_name": "leader_retention_state",
                "feature_family": "dynamic_role_core",
                "reading": "Tracks whether the initial leader remains the market's leadership anchor after diffusion begins.",
                "best_used_for": "distinguishing durable leaders from short-lived ignition leaders",
                "status": "review_only_dynamic_feature_candidate",
            },
            {
                "feature_name": "challenger_activation_state",
                "feature_family": "dynamic_role_extension",
                "reading": "Captures when adjacent objects move from passive relevance to active diffusion participation.",
                "best_used_for": "early diffusion and secondary beta selection",
                "status": "review_only_dynamic_feature_candidate",
            },
            {
                "feature_name": "role_demotion_risk_state",
                "feature_family": "dynamic_role_risk",
                "reading": "Captures whether an object is losing role quality during divergence, even if price has not fully broken yet.",
                "best_used_for": "avoiding false continuation during high-level decay",
                "status": "review_only_dynamic_feature_candidate",
            },
            {
                "feature_name": "branch_upgrade_state",
                "feature_family": "dynamic_role_extension",
                "reading": "Measures when branch rows gain strategic relevance because route depth, packaging, or advanced component discussion strengthens.",
                "best_used_for": "re-ignition and route-depth windows",
                "status": "review_only_dynamic_feature_candidate",
            },
            {
                "feature_name": "role_requalification_state",
                "feature_family": "dynamic_role_core",
                "reading": "Marks the stage where previously proven core or challenger rows regain admissible strength after a long quiet window.",
                "best_used_for": "second-wave and third-wave restart recognition",
                "status": "review_only_dynamic_feature_candidate",
            },
            {
                "feature_name": "spillover_saturation_state",
                "feature_family": "dynamic_role_overlay",
                "reading": "Marks when spillover and late-extension activity stop adding breadth information and start indicating maturity or exhaustion.",
                "best_used_for": "late-cycle risk overlays and maturity detection",
                "status": "review_only_dynamic_feature_candidate",
            },
            {
                "feature_name": "residual_core_strength_state",
                "feature_family": "dynamic_role_core",
                "reading": "Separates the rows that still hold structural importance after catch-up and decay from those only participating in final noise.",
                "best_used_for": "late-cycle defense and residual core concentration",
                "status": "review_only_dynamic_feature_candidate",
            },
            {
                "feature_name": "spillover_collapse_risk_state",
                "feature_family": "dynamic_role_overlay",
                "reading": "Captures the moment when late-cycle spillover is more likely to unwind than continue.",
                "best_used_for": "drawdown control and avoiding weak late followers",
                "status": "review_only_dynamic_feature_candidate",
            },
            {
                "feature_name": "role_transition_confidence_state",
                "feature_family": "dynamic_role_meta",
                "reading": "A review-only confidence layer informed by unresolved mixed clusters and pending rows.",
                "best_used_for": "keeping later label draft honest around ambiguous role changes",
                "status": "review_only_dynamic_feature_candidate",
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112ad_dynamic_role_transition_feature_review_v1",
            "transition_event_count": len(transition_event_rows),
            "dynamic_feature_count": len(dynamic_feature_rows),
            "role_change_is_time_conditioned": True,
            "formal_feature_promotion_still_forbidden": True,
            "formal_label_freeze_still_forbidden": True,
            "formal_training_still_forbidden": True,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "Static role labels are not enough for a cycle with re-ignition, challenger activation, late spillover, and final decay.",
            "These features make role migration explicit without turning role change into a backfilled truth claim.",
            "The correct next use is bounded review and later feature-family design, not automatic training promotion.",
        ]
        return V112ADDynamicRoleTransitionFeatureReviewReport(
            summary=summary,
            transition_event_rows=transition_event_rows,
            dynamic_feature_rows=dynamic_feature_rows,
            interpretation=interpretation,
        )


def write_v112ad_dynamic_role_transition_feature_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ADDynamicRoleTransitionFeatureReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
