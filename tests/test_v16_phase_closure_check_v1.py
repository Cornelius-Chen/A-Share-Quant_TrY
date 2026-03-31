from __future__ import annotations

from a_share_quant.strategy.v16_phase_closure_check_v1 import V16PhaseClosureCheckAnalyzer


def test_v16_phase_closure_check_enters_waiting_state_after_bounded_stability_success() -> None:
    result = V16PhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v16_now": True, "acceptance_posture": "open_v16_provisional_candidacy_stability_review"}},
        feature_stability_review_payload={"summary": {"continue_provisional_candidacy_count": 4, "hold_for_more_stability_evidence_count": 0, "drop_from_provisional_candidacy_count": 0}},
        phase_check_payload={"summary": {"acceptance_posture": "keep_v16_active_but_bounded_as_stability_review", "promote_retained_now": False, "do_integrate_into_strategy_now": False}},
    )

    assert result.summary["acceptance_posture"] == "close_v16_as_bounded_stability_review_success"
    assert result.summary["v16_success_criteria_met"] is True
    assert result.summary["enter_v16_waiting_state_now"] is True
