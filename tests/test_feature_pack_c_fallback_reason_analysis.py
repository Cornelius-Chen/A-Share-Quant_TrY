from __future__ import annotations

from a_share_quant.strategy.feature_pack_c_fallback_reason_analysis import (
    FeaturePackCFallbackReasonAnalyzer,
)


def test_feature_pack_c_fallback_reason_analysis_prefers_late_quality_when_it_dominates() -> None:
    payload = {
        "case_rows": [
            {
                "case_name": "a",
                "trigger_date": "2024-01-01",
                "mechanism_type": "entry_suppression_avoidance",
                "challenger_assignment_reason": "fallback_to_junk",
                "challenger_late_quality_margin": -0.08,
                "challenger_non_junk_margin": -0.01,
                "challenger_resonance_margin": 0.02,
                "challenger_top_score_gap": 0.3,
                "challenger_margin_gap": -0.02,
                "concept_support": 0.0,
                "fallback_reason_score": 0.08,
            },
            {
                "case_name": "b",
                "trigger_date": "2024-01-02",
                "mechanism_type": "entry_suppression_avoidance",
                "challenger_assignment_reason": "low_composite_or_low_resonance",
                "challenger_late_quality_margin": -0.05,
                "challenger_non_junk_margin": -0.02,
                "challenger_resonance_margin": -0.01,
                "challenger_top_score_gap": 0.1,
                "challenger_margin_gap": 0.05,
                "concept_support": 0.3,
                "fallback_reason_score": 0.02,
            },
        ]
    }

    result = FeaturePackCFallbackReasonAnalyzer().analyze(
        recheck_payload=payload,
        case_names=["a", "b"],
    )

    assert result.summary["row_count"] == 2
    assert result.summary["dominant_component_counts"]["late_quality"] == 2
    assert result.summary["approval_edge_active_count"] == 1
    assert result.summary["recommended_first_feature_group"] == "fallback_reason_decomposition_plus_late_quality_residuals"
