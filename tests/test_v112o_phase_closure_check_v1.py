from __future__ import annotations

from a_share_quant.strategy.v112o_phase_closure_check_v1 import (
    V112OPhaseClosureCheckAnalyzer,
)


def test_v112o_phase_closure_enters_waiting_state() -> None:
    result = V112OPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload={
            "summary": {
                "ready_for_phase_closure_next": True,
                "selected_archetype": "optical_link_price_and_demand_upcycle",
                "validated_local_seed_count": 3,
                "review_only_adjacent_candidate_count": 6,
            }
        }
    )

    assert result.summary["v112o_success_criteria_met"] is True
    assert result.summary["enter_v112o_waiting_state_now"] is True
