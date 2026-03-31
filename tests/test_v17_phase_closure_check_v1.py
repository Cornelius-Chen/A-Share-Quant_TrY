from __future__ import annotations

from a_share_quant.strategy.v17_phase_closure_check_v1 import V17PhaseClosureCheckAnalyzer


def test_v17_phase_closure_check_enters_waiting_state_after_bounded_gap_success() -> None:
    result = V17PhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {"do_open_v17_now": True, "acceptance_posture": "open_v17_promotion_evidence_generation"}
        },
        feature_promotion_gap_review_payload={
            "summary": {
                "reviewed_feature_count": 4,
                "promotion_ready_now_count": 0,
                "needs_additional_promotion_evidence_count": 4,
            }
        },
        phase_check_payload={
            "summary": {
                "acceptance_posture": "keep_v17_active_but_bounded_as_promotion_evidence_generation",
                "promote_retained_now": False,
                "do_integrate_into_strategy_now": False,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "close_v17_as_bounded_promotion_evidence_generation_success"
    assert result.summary["v17_success_criteria_met"] is True
    assert result.summary["enter_v17_waiting_state_now"] is True
