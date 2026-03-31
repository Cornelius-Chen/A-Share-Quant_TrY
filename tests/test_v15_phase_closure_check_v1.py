from __future__ import annotations

from a_share_quant.strategy.v15_phase_closure_check_v1 import V15PhaseClosureCheckAnalyzer


def test_v15_phase_closure_check_enters_waiting_state_after_bounded_review_success() -> None:
    result = V15PhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v15_now": True, "acceptance_posture": "open_v15_retained_feature_candidacy_review"}},
        feature_admissibility_review_payload={"summary": {"allow_provisional_candidacy_review_count": 4, "hold_for_more_evidence_count": 1, "reject_candidacy_count": 0}},
        phase_check_payload={"summary": {"acceptance_posture": "keep_v15_active_but_bounded_as_candidacy_review", "promote_retained_now": False, "do_integrate_into_strategy_now": False}},
    )

    assert result.summary["acceptance_posture"] == "close_v15_as_bounded_candidacy_review_success"
    assert result.summary["v15_success_criteria_met"] is True
    assert result.summary["enter_v15_waiting_state_now"] is True
