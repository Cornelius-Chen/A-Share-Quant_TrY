from __future__ import annotations

from a_share_quant.strategy.u2_pocket_clustering_readiness import U2PocketClusteringReadinessAnalyzer


def test_u2_readiness_holds_when_suspect_set_is_small_and_separable() -> None:
    result = U2PocketClusteringReadinessAnalyzer().analyze(
        feature_gap_payload={
            "summary": {
                "feature_gap_suspect_count": 2,
                "thinning_signal": True,
            }
        },
        feature_pack_c_acceptance_payload={
            "summary": {
                "acceptance_posture": "close_feature_pack_c_as_explanatory_and_prepare_u1_sidecar",
                "ready_for_u1_lightweight_geometry": True,
            }
        },
        u1_payload={
            "summary": {
                "case_centroid_distance": 4.080383,
                "separation_reading": "cases_geometrically_separable",
            }
        },
    )

    assert result.summary["u2_ready"] is False
    assert result.summary["recommended_next_phase"] == "hold_u2_and_wait_for_larger_or_less_separable_suspect_set"
