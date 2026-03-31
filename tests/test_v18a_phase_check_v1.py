from __future__ import annotations

from a_share_quant.strategy.v18a_phase_check_v1 import V18APhaseCheckAnalyzer


def test_v18a_phase_check_keeps_branch_bounded_after_entry_design() -> None:
    result = V18APhaseCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {
                "do_open_v18a_now": True,
                "sample_breadth_target_feature_count": 2,
                "target_feature_names": ["single_pulse_support", "policy_followthrough_support"],
            }
        },
        breadth_entry_design_payload={
            "summary": {"entry_row_count": 2, "allow_unbounded_sample_collection_now": False}
        },
    )

    assert result.summary["acceptance_posture"] == "keep_v18a_active_but_bounded_as_sample_breadth_expansion_design"
    assert result.summary["v18a_open"] is True
    assert result.summary["collect_samples_now"] is False
