from __future__ import annotations

from a_share_quant.strategy.feature_pack_c_readiness import FeaturePackCReadinessAnalyzer


def test_feature_pack_c_readiness_prefers_local_causal_edges_after_two_closed_tracks() -> None:
    result = FeaturePackCReadinessAnalyzer().analyze(
        feature_gap_payload={
            "summary": {
                "feature_gap_suspect_count": 2,
                "thinning_signal": True,
            }
        },
        track_a_payload={
            "summary": {
                "case_name": "theme_q4_002902_b",
                "dominant_hierarchy_edge": "late_mover_quality",
                "dominant_approval_edge": "score_margin_threshold",
            }
        },
        track_a_sweep_payload={
            "candidate_rows": [
                {
                    "candidate_name": "theme_margin_relief_003",
                    "repair_profile": "permission_led",
                    "total_pnl": -177.915,
                }
            ]
        },
        track_b_payload={
            "summary": {
                "case_name": "theme_q2_002466_c",
                "dominant_bridge": "concept_to_late_mover",
                "late_quality_straddles": 2,
                "concept_supported_late_rows": 2,
            }
        },
        track_b_validation_payload={
            "summary": {
                "best_variant_name": "v2_broad_concept_late_bridge",
                "best_variant_alpha_retention_ratio": 0.175228,
                "best_variant_repair_completion_ratio": 0.5,
                "acceptance_posture": "close_track_b_as_negative_informative",
            }
        },
    )

    assert result.summary["recommended_next_phase"] == "feature_pack_c_local_causal_edges"
    assert result.summary["do_restart_replay_queue"] is False
    assert result.summary["track_b_closed"] is True
    assert result.recommended_features[0]["feature_name"] == "fallback_reason_decomposition"
