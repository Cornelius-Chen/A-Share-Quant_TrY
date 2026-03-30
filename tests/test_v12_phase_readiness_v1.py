from __future__ import annotations

from a_share_quant.strategy.v12_phase_readiness_v1 import V12PhaseReadinessAnalyzer


def test_v12_phase_readiness_keeps_phase_open_when_row_diversity_missing() -> None:
    data_audit_payload = {"summary": {"baseline_ready": True, "canonical_ready_count": 6, "derived_ready_count": 3}}
    registry_payload = {"summary": {"ready_for_factor_evaluation_protocol": True}}
    factorization_review_payload = {
        "summary": {
            "v12_factorization_milestone_reached": True,
            "do_open_second_factor_lane_now": False,
        }
    }
    carry_pilot_payload = {
        "summary": {
            "pilot_mode": "report_only_micro_pilot",
            "needs_more_row_diversity_for_rankable_pilot": True,
            "allow_rankable_pilot_now": False,
        }
    }

    result = V12PhaseReadinessAnalyzer().analyze(
        data_audit_payload=data_audit_payload,
        registry_payload=registry_payload,
        factorization_review_payload=factorization_review_payload,
        carry_pilot_payload=carry_pilot_payload,
    )

    assert (
        result.summary["acceptance_posture"]
        == "keep_v12_open_and_wait_for_new_refresh_batch_or_row_diversity"
    )
    assert result.summary["ready_to_close_v12_now"] is False
    assert result.summary["do_open_new_refresh_batch_now"] is True


def test_v12_phase_readiness_can_close_when_no_diversity_gap_remains() -> None:
    data_audit_payload = {"summary": {"baseline_ready": True}}
    registry_payload = {"summary": {"ready_for_factor_evaluation_protocol": True}}
    factorization_review_payload = {
        "summary": {
            "v12_factorization_milestone_reached": True,
            "do_open_second_factor_lane_now": False,
        }
    }
    carry_pilot_payload = {
        "summary": {
            "pilot_mode": "rankable_micro_pilot",
            "needs_more_row_diversity_for_rankable_pilot": False,
            "allow_rankable_pilot_now": True,
        }
    }

    result = V12PhaseReadinessAnalyzer().analyze(
        data_audit_payload=data_audit_payload,
        registry_payload=registry_payload,
        factorization_review_payload=factorization_review_payload,
        carry_pilot_payload=carry_pilot_payload,
    )

    assert result.summary["acceptance_posture"] == "close_v12_as_first_bounded_data_plus_factorization_phase"
    assert result.summary["ready_to_close_v12_now"] is True
