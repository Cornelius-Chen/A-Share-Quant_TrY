from __future__ import annotations

from a_share_quant.strategy.feature_pack_c_acceptance import FeaturePackCAcceptanceAnalyzer


def test_feature_pack_c_acceptance_closes_when_turnover_lane_is_sector_masked() -> None:
    result = FeaturePackCAcceptanceAnalyzer().analyze(
        fallback_payload={
            "summary": {
                "dominant_component_counts": {
                    "late_quality": 6,
                    "score_margin": 2,
                }
            }
        },
        residual_payload={
            "summary": {
                "raw_below_threshold_count": 8,
                "concept_boost_active_count": 1,
                "dominant_residual_component_counts": {
                    "stability": 3,
                    "liquidity": 3,
                    "sector_strength": 2,
                },
            }
        },
        stability_liquidity_payload={
            "summary": {
                "local_context_counts": {
                    "turnover_share_led": 3,
                    "mixed_stability_liquidity": 3,
                }
            }
        },
        turnover_payload={
            "summary": {
                "local_turnover_context_counts": {
                    "sector_peer_dominance": 1,
                    "broad_attention_deficit": 0,
                    "balanced_share_weakness": 2,
                }
            }
        },
        balanced_turnover_payload={
            "summary": {
                "balanced_weakness_counts": {
                    "singleton_sector_masking": 2,
                    "true_balanced_share_weakness": 0,
                }
            }
        },
    )

    assert result.summary["acceptance_posture"] == "close_feature_pack_c_as_explanatory_and_prepare_u1_sidecar"
    assert result.summary["do_continue_pack_c_turnover_branch"] is False
    assert result.summary["ready_for_u1_lightweight_geometry"] is True
