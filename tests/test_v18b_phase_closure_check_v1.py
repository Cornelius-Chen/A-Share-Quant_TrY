from __future__ import annotations

from a_share_quant.strategy.v18b_phase_closure_check_v1 import V18BPhaseClosureCheckAnalyzer


def test_v18b_phase_closure_check_enters_waiting_state_after_bounded_gate_success() -> None:
    result = V18BPhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {
                "do_open_v18b_now": True,
                "acceptance_posture": "open_v18b_breadth_sample_admission_gate",
            }
        },
        feature_admission_gate_review_payload={
            "summary": {
                "reviewed_feature_count": 2,
                "admission_gate_ready_count": 2,
                "allow_sample_collection_now": False,
            }
        },
        phase_check_payload={
            "summary": {
                "acceptance_posture": "keep_v18b_active_but_bounded_as_admission_gate_review",
                "allow_sample_collection_now": False,
                "promote_retained_now": False,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "close_v18b_as_bounded_admission_gate_success"
    assert result.summary["v18b_success_criteria_met"] is True
    assert result.summary["enter_v18b_waiting_state_now"] is True
