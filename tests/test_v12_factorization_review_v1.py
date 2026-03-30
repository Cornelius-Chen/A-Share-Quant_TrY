from __future__ import annotations

from a_share_quant.strategy.v12_factorization_review_v1 import (
    V12FactorizationReviewAnalyzer,
)


def test_v12_factorization_review_closes_first_cycle_as_bounded_success() -> None:
    registry_payload = {"summary": {"ready_for_factor_evaluation_protocol": True, "candidate_factor_count": 3}}
    protocol_payload = {
        "summary": {
            "ready_for_first_pass_factor_evaluation": True,
            "evaluate_now_count": 1,
            "evaluate_with_penalty_count": 1,
            "hold_for_more_sample_count": 1,
            "penalty_shortlist": ["preemptive_loss_avoidance_shift"],
            "deferred_shortlist": ["delayed_entry_basis_advantage"],
        }
    }
    carry_first_pass_payload = {"summary": {"do_open_bounded_carry_factor_lane": True}}
    carry_pilot_payload = {
        "summary": {
            "allow_report_only_pilot_now": True,
            "allow_rankable_pilot_now": False,
            "pilot_mode": "report_only_micro_pilot",
        }
    }

    result = V12FactorizationReviewAnalyzer().analyze(
        registry_payload=registry_payload,
        protocol_payload=protocol_payload,
        carry_first_pass_payload=carry_first_pass_payload,
        carry_pilot_payload=carry_pilot_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "close_first_v12_factorization_cycle_as_representative_but_bounded"
    )
    assert result.summary["v12_factorization_milestone_reached"] is True
    assert result.summary["do_open_second_factor_lane_now"] is False


def test_v12_factorization_review_stays_open_if_carry_pilot_not_open() -> None:
    registry_payload = {"summary": {"ready_for_factor_evaluation_protocol": True, "candidate_factor_count": 3}}
    protocol_payload = {"summary": {"ready_for_first_pass_factor_evaluation": True}}
    carry_first_pass_payload = {"summary": {"do_open_bounded_carry_factor_lane": True}}
    carry_pilot_payload = {"summary": {"allow_report_only_pilot_now": False, "allow_rankable_pilot_now": False}}

    result = V12FactorizationReviewAnalyzer().analyze(
        registry_payload=registry_payload,
        protocol_payload=protocol_payload,
        carry_first_pass_payload=carry_first_pass_payload,
        carry_pilot_payload=carry_pilot_payload,
    )

    assert result.summary["acceptance_posture"] == "continue_v12_factorization_cycle"
    assert result.summary["v12_factorization_milestone_reached"] is False
