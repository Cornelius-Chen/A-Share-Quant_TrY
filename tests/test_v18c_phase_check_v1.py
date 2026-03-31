from __future__ import annotations

from a_share_quant.strategy.v18c_phase_check_v1 import V18CPhaseCheckAnalyzer


def test_v18c_phase_check_keeps_branch_bounded_after_collection() -> None:
    result = V18CPhaseCheckAnalyzer().analyze(
        phase_charter_payload={
            "summary": {
                "do_open_v18c_now": True,
                "target_feature_names": ["single_pulse_support", "policy_followthrough_support"],
            }
        },
        screened_collection_payload={
            "summary": {
                "target_feature_count": 2,
                "admitted_case_count": 3,
                "targets_with_admitted_cases_count": 2,
                "sample_limit_breaches": 0,
            }
        },
    )

    assert result.summary["acceptance_posture"] == "keep_v18c_active_but_bounded_as_screened_collection"
    assert result.summary["v18c_open"] is True
    assert result.summary["promote_retained_now"] is False
