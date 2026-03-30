from __future__ import annotations

from a_share_quant.strategy.v12_batch_substrate_decision_v1 import (
    V12BatchSubstrateDecisionAnalyzer,
)


def test_v12_batch_substrate_decision_prepares_new_refresh() -> None:
    phase_readiness_payload = {
        "summary": {
            "row_diversity_still_missing": True,
            "do_open_new_refresh_batch_now": True,
        }
    }
    v4_reassessment_payload = {
        "summary": {
            "v4_still_active_substrate": True,
            "checked_region_paused": True,
        }
    }
    specialist_analysis_payload = {
        "top_opportunities": [
            {"dataset_name": "market_research_v3_factor_diversity_seed", "slice_name": "2024_q4"},
            {"dataset_name": "market_research_v4_carry_row_diversity_refresh", "slice_name": "2024_q2"},
        ]
    }

    result = V12BatchSubstrateDecisionAnalyzer().analyze(
        phase_readiness_payload=phase_readiness_payload,
        v4_reassessment_payload=v4_reassessment_payload,
        specialist_analysis_payload=specialist_analysis_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "prepare_next_refresh_batch_instead_of_reopening_existing_local_substrate"
    )
    assert result.summary["do_prepare_new_refresh_batch_now"] is True
    assert result.summary["do_reopen_v3_local_lane_now"] is False
    assert result.summary["do_reopen_v4_local_lane_now"] is False
