from __future__ import annotations

from a_share_quant.strategy.v112p_phase_check_v1 import V112PPhaseCheckAnalyzer


def test_v112p_phase_check_keeps_registry_boundary() -> None:
    result = V112PPhaseCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {
                "do_open_v112p_now": True,
                "selected_archetype": "optical_link_price_and_demand_upcycle",
            }
        },
        registry_payload={
            "summary": {
                "information_layer_count": 6,
                "cohort_row_count": 20,
                "source_count": 10,
                "remaining_gap_count": 4,
            }
        },
    )

    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["allow_auto_feature_promotion_now"] is False
