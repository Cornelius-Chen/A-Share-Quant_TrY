from __future__ import annotations

from a_share_quant.strategy.v110a_phase_closure_check_v1 import V110APhaseClosureCheckAnalyzer


def test_v110a_phase_closure_check_enters_waiting_state_after_single_probe() -> None:
    result = V110APhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v110a_now": True, "acceptance_posture": "open_v110a_policy_followthrough_cross_family_breadth_probe"}},
        cross_family_probe_payload={
            "summary": {
                "candidate_count": 2,
                "admitted_case_count": 0,
                "successful_negative_probe": True,
            }
        },
        phase_check_payload={
            "summary": {
                "acceptance_posture": "keep_v110a_single_probe_bounded_and_non_expanding",
                "open_follow_on_probe_now": False,
                "promote_retained_now": False,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "close_v110a_as_single_cross_family_probe_success"
    assert result.summary["enter_v110a_waiting_state_now"] is True
