from __future__ import annotations

from a_share_quant.strategy.v112o_phase_check_v1 import V112OPhaseCheckAnalyzer


def test_v112o_phase_check_keeps_scope_freeze_boundary() -> None:
    result = V112OPhaseCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {
                "do_open_v112o_now": True,
                "selected_archetype": "optical_link_price_and_demand_upcycle",
            }
        },
        study_scope_payload={
            "summary": {
                "validated_local_seed_count": 3,
                "review_only_adjacent_candidate_count": 6,
                "bounded_study_dimension_count": 8,
            }
        },
    )

    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["allow_auto_dataset_widening_now"] is False
