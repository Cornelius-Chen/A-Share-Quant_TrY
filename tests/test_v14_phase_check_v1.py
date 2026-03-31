from __future__ import annotations

from a_share_quant.strategy.v14_phase_check_v1 import V14PhaseCheckAnalyzer


def test_v14_phase_check_keeps_branch_bounded_after_positive_discrimination() -> None:
    result = V14PhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v14_now": True, "acceptance_posture": "open_v14_context_consumption_pilot", "recommended_first_action": "freeze_v14_context_consumption_protocol_v1"}},
        bounded_discrimination_payload={"summary": {"acceptance_posture": "open_v14_bounded_discrimination_check_v1_as_report_only_review", "stable_discrimination_present": True, "promote_context_now": False}},
    )

    assert result.summary["acceptance_posture"] == "keep_v14_active_but_bounded_as_context_consumption_pilot"
    assert result.summary["v14_open"] is True
    assert result.summary["stable_discrimination_present"] is True
    assert result.summary["do_integrate_into_strategy_now"] is False
