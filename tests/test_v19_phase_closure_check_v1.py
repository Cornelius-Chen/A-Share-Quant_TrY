from __future__ import annotations

from a_share_quant.strategy.v19_phase_closure_check_v1 import V19PhaseClosureCheckAnalyzer


def test_v19_phase_closure_check_enters_waiting_state_after_bounded_rereview() -> None:
    result = V19PhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {"do_open_v19_now": True, "acceptance_posture": "open_v19_breadth_evidence_rereview"}
        },
        feature_breadth_rereview_payload={
            "summary": {
                "reviewed_feature_count": 2,
                "shortfall_changed_count": 1,
                "breadth_gap_materially_reduced_count": 1,
                "breadth_gap_partially_reduced_count": 1,
                "promotion_ready_now_count": 0,
            }
        },
        phase_check_payload={
            "summary": {
                "acceptance_posture": "keep_v19_active_but_bounded_as_breadth_evidence_rereview",
                "promote_retained_now": False,
                "do_integrate_into_strategy_now": False,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "close_v19_as_bounded_breadth_evidence_rereview_success"
    assert result.summary["v19_success_criteria_met"] is True
    assert result.summary["enter_v19_waiting_state_now"] is True
