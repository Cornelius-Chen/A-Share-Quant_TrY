from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BDMarketRegimeOverlayFeatureReviewReport:
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


class V112BDMarketRegimeOverlayFeatureReviewAnalyzer:
    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        v112af_feature_family_payload: dict[str, Any],
        v113c_state_usage_payload: dict[str, Any],
    ) -> V112BDMarketRegimeOverlayFeatureReviewReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112bd_now")):
            raise ValueError("V1.12BD must be open before overlay review.")

        feature_family_summary = dict(v112af_feature_family_payload.get("summary", {}))
        state_usage_summary = dict(v113c_state_usage_payload.get("summary", {}))
        if not bool(feature_family_summary.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BD expects the CPO feature-family design layer from V1.12AF.")
        if not bool(state_usage_summary.get("ready_for_phase_check_next")):
            raise ValueError("V1.12BD expects the bounded state-usage review from V1.13C.")

        overlay_feature_rows = [
            {"feature_name": "broad_index_trend_state", "overlay_domain": "index_trend", "allowed_usage_layer": "market_regime_overlay_only"},
            {"feature_name": "all_market_turnover_liquidity_state", "overlay_domain": "liquidity", "allowed_usage_layer": "market_regime_overlay_only"},
            {"feature_name": "risk_appetite_heat_state", "overlay_domain": "risk_appetite", "allowed_usage_layer": "market_regime_overlay_only"},
            {"feature_name": "chinext_relative_strength_state", "overlay_domain": "board_style", "allowed_usage_layer": "market_regime_overlay_only"},
            {"feature_name": "star_board_relative_strength_state", "overlay_domain": "board_style", "allowed_usage_layer": "market_regime_overlay_only"},
            {"feature_name": "ai_hardware_cross_board_resonance_state", "overlay_domain": "cross_board_resonance", "allowed_usage_layer": "market_regime_overlay_only"},
            {"feature_name": "optics_sector_etf_strength_state", "overlay_domain": "sector_etf", "allowed_usage_layer": "market_regime_overlay_only"},
            {"feature_name": "turnover_pressure_overlay_state", "overlay_domain": "turnover_pressure", "allowed_usage_layer": "market_regime_overlay_only"},
            {"feature_name": "liquidity_dispersion_state", "overlay_domain": "liquidity", "allowed_usage_layer": "market_regime_overlay_only"},
            {"feature_name": "sector_rotation_conflict_state", "overlay_domain": "rotation_conflict", "allowed_usage_layer": "market_regime_overlay_only"},
        ]
        family_rows = [
            {
                "family_name": "market_regime_overlay_family",
                "family_posture": "design_ready_overlay_family",
                "member_count": len(overlay_feature_rows),
                "disallowed_layers": ["core_truth_label", "role_truth_replacement", "formal_signal_trigger"],
                "reading": "These factors may amplify or suppress a cycle, but they do not replace stock-level role and catalyst truth.",
            }
        ]

        summary = {
            "acceptance_posture": "freeze_v112bd_market_regime_overlay_feature_review_v1",
            "overlay_feature_count": len(overlay_feature_rows),
            "overlay_family_count": len(family_rows),
            "board_style_feature_count": 2,
            "sector_etf_feature_count": 1,
            "liquidity_feature_count": 2,
            "formal_feature_promotion_now": False,
            "formal_label_promotion_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "V1.12BD freezes broad-market, board-style, and sector-ETF context as an overlay family rather than as core truth.",
            "This allows later experiments to test regime amplification without flattening the CPO cycle grammar into market beta.",
        ]
        return V112BDMarketRegimeOverlayFeatureReviewReport(
            summary=summary,
            overlay_feature_rows=overlay_feature_rows,
            family_rows=family_rows,
            interpretation=interpretation,
        )


def write_v112bd_market_regime_overlay_feature_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BDMarketRegimeOverlayFeatureReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
