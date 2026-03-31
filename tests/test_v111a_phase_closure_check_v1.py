from __future__ import annotations

from a_share_quant.strategy.v111a_phase_closure_check_v1 import (
    V111APhaseClosureCheckAnalyzer,
)


def test_v111a_phase_closure_check_closes_after_one_successful_bounded_pilot() -> None:
    result = V111APhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v111a_now": True}},
        screened_first_collection_payload={
            "summary": {
                "admitted_candidate_count": 2,
                "admitted_policy_followthrough_count": 0,
                "sample_limit_breaches": 0,
            }
        },
        phase_check_payload={"summary": {"allow_retained_promotion_now": False}},
    )

    assert result.summary["v111a_success_criteria_met"] is True
    assert result.summary["enter_v111a_waiting_state_now"] is True
    assert result.summary["allow_auto_follow_on_now"] is False
