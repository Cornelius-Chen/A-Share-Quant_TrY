from __future__ import annotations

from a_share_quant.strategy.v112p_phase_closure_check_v1 import (
    V112PPhaseClosureCheckAnalyzer,
)


def test_v112p_phase_closure_enters_waiting_state() -> None:
    result = V112PPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload={
            "summary": {
                "ready_for_phase_closure_next": True,
                "selected_archetype": "optical_link_price_and_demand_upcycle",
                "cohort_row_count": 20,
                "source_count": 10,
                "remaining_gap_count": 4,
            }
        }
    )

    assert result.summary["v112p_success_criteria_met"] is True
    assert result.summary["enter_v112p_waiting_state_now"] is True
