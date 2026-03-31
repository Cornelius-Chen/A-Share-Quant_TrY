from __future__ import annotations

from a_share_quant.strategy.v18b_phase_check_v1 import V18BPhaseCheckAnalyzer


def test_v18b_phase_check_keeps_branch_bounded_after_gate_review() -> None:
    result = V18BPhaseCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {
                "do_open_v18b_now": True,
                "target_feature_names": ["single_pulse_support", "policy_followthrough_support"],
            }
        },
        feature_admission_gate_review_payload={
            "summary": {
                "reviewed_feature_count": 2,
                "admission_gate_ready_count": 2,
                "allow_sample_collection_now": False,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "keep_v18b_active_but_bounded_as_admission_gate_review"
    assert result.summary["v18b_open"] is True
    assert result.summary["allow_sample_collection_now"] is False
