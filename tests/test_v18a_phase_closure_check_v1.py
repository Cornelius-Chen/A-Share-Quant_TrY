from __future__ import annotations

from a_share_quant.strategy.v18a_phase_closure_check_v1 import V18APhaseClosureCheckAnalyzer


def test_v18a_phase_closure_check_enters_waiting_state_after_bounded_entry_design() -> None:
    result = V18APhaseClosureCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {
                "do_open_v18a_now": True,
                "sample_breadth_target_feature_count": 2,
                "acceptance_posture": "open_v18a_sample_breadth_expansion",
            }
        },
        breadth_entry_design_payload={
            "summary": {"entry_row_count": 2, "allow_unbounded_sample_collection_now": False}
        },
        phase_check_payload={
            "summary": {
                "acceptance_posture": "keep_v18a_active_but_bounded_as_sample_breadth_expansion_design",
                "collect_samples_now": False,
                "promote_retained_now": False,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "close_v18a_as_bounded_sample_breadth_expansion_success"
    assert result.summary["v18a_success_criteria_met"] is True
    assert result.summary["enter_v18a_waiting_state_now"] is True
