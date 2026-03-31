from __future__ import annotations

from a_share_quant.strategy.v111a_phase_check_v1 import V111APhaseCheckAnalyzer


def test_v111a_phase_check_distinguishes_path_validation_from_direct_followthrough_gain() -> None:
    result = V111APhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v111a_now": True}},
        screened_first_collection_payload={
            "summary": {
                "admitted_candidate_count": 2,
                "admitted_policy_followthrough_count": 0,
            }
        },
    )

    assert result.summary["acquisition_path_validated"] is True
    assert result.summary["direct_policy_followthrough_breadth_gain_present"] is False
    assert result.summary["allow_retained_promotion_now"] is False
