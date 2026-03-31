from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BOCPOInternalMaturityOverlayReviewReport:
    summary: dict[str, Any]
    overlay_feature_rows: list[dict[str, Any]]
    family_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "overlay_feature_rows": self.overlay_feature_rows,
            "family_rows": self.family_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BOCPOInternalMaturityOverlayReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
        market_regime_overlay_payload: dict[str, Any],
        feature_family_payload: dict[str, Any],
        regime_gate_pilot_payload: dict[str, Any],
    ) -> V112BOCPOInternalMaturityOverlayReviewReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112bo_now")):
            raise ValueError("V1.12BO must be open before internal maturity overlay review.")
        if not bool(dict(cycle_reconstruction_payload.get("summary", {})).get("cycle_absorption_review_success")):
            raise ValueError("V1.12BO expects the bounded cycle reconstruction layer.")
        if not bool(dict(market_regime_overlay_payload.get("summary", {})).get("ready_for_phase_check_next")):
            raise ValueError("V1.12BO expects the frozen market regime overlay family.")
        if not bool(dict(feature_family_payload.get("summary", {})).get("ready_for_phase_check_next")):
            raise ValueError("V1.12BO expects the CPO feature family layer from V1.12AF.")
        if not bool(dict(regime_gate_pilot_payload.get("summary", {})).get("ready_for_phase_check_next")):
            raise ValueError("V1.12BO expects the bounded regime-aware gate pilot result.")

        overlay_feature_rows = [
            {
                "feature_name": "core_branch_relative_strength_spread_state",
                "overlay_domain": "internal_relative_strength",
                "allowed_usage_layer": "internal_maturity_overlay_only",
                "reading": "Measures whether core names still dominate branch rows or whether branch beta has started to overtake core quality.",
            },
            {
                "feature_name": "core_spillover_divergence_state",
                "overlay_domain": "spillover_divergence",
                "allowed_usage_layer": "internal_maturity_overlay_only",
                "reading": "Measures whether spillover activation is exceeding core-strength confirmation, a common late-maturity warning.",
            },
            {
                "feature_name": "internal_breadth_compression_state",
                "overlay_domain": "breadth_compression",
                "allowed_usage_layer": "internal_maturity_overlay_only",
                "reading": "Tracks whether internal participation is shrinking from broad diffusion back to a narrow set of survivors.",
            },
            {
                "feature_name": "internal_turnover_concentration_state",
                "overlay_domain": "turnover_concentration",
                "allowed_usage_layer": "internal_maturity_overlay_only",
                "reading": "Tracks whether turnover is concentrating into a smaller subset of names, often a congestion warning.",
            },
            {
                "feature_name": "leader_absorption_fragility_state",
                "overlay_domain": "leader_absorption",
                "allowed_usage_layer": "internal_maturity_overlay_only",
                "reading": "Tracks whether the leader still absorbs pressure cleanly or begins to show maturity-stage fragility.",
            },
            {
                "feature_name": "branch_promotion_failure_rate_state",
                "overlay_domain": "branch_quality",
                "allowed_usage_layer": "internal_maturity_overlay_only",
                "reading": "Tracks whether branch names can sustain promotion from review support into credible extension or repeatedly fail.",
            },
            {
                "feature_name": "role_deterioration_spread_state",
                "overlay_domain": "role_deterioration",
                "allowed_usage_layer": "internal_maturity_overlay_only",
                "reading": "Tracks whether more rows are being downgraded from core or extension roles into weaker maturity-stage behavior.",
            },
            {
                "feature_name": "spillover_saturation_overlay_state",
                "overlay_domain": "spillover_saturation",
                "allowed_usage_layer": "internal_maturity_overlay_only",
                "reading": "Tracks whether late-stage spillover activation has reached levels more consistent with maturity than with healthy diffusion.",
            },
        ]
        family_rows = [
            {
                "family_name": "cpo_internal_maturity_overlay_family",
                "family_posture": "design_ready_overlay_family",
                "member_count": len(overlay_feature_rows),
                "disallowed_layers": ["core_truth_label", "role_truth_replacement", "formal_signal_trigger"],
                "reading": (
                    "These factors express internal crowding, maturity, and role-quality deterioration inside the CPO cohort. "
                    "They can filter later portfolio decisions but do not replace role, phase, or catalyst truth."
                ),
            }
        ]
        summary = {
            "acceptance_posture": "freeze_v112bo_cpo_internal_maturity_overlay_review_v1",
            "overlay_feature_count": len(overlay_feature_rows),
            "overlay_family_count": len(family_rows),
            "relative_strength_feature_count": 2,
            "breadth_turnover_feature_count": 2,
            "role_quality_feature_count": 3,
            "spillover_feature_count": 1,
            "formal_feature_promotion_now": False,
            "formal_label_promotion_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "use_internal_maturity_overlay_in_later_gate_or_selector_fusion_before_any_large_data_widen",
        }
        interpretation = [
            "V1.12BO freezes the missing layer between market regime and stock-level truth: internal maturity, congestion, and role-quality deterioration inside the CPO cohort.",
            "This layer is explicitly motivated by the BL failure: regime alone was necessary but insufficient.",
        ]
        return V112BOCPOInternalMaturityOverlayReviewReport(
            summary=summary,
            overlay_feature_rows=overlay_feature_rows,
            family_rows=family_rows,
            interpretation=interpretation,
        )


def write_v112bo_cpo_internal_maturity_overlay_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BOCPOInternalMaturityOverlayReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
