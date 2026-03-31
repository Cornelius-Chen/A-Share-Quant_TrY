from __future__ import annotations

from a_share_quant.strategy.v112e_phase_check_v1 import V112EPhaseCheckAnalyzer


def test_v112e_phase_check_stays_report_only() -> None:
    result = V112EPhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112e_now": True}},
        attribution_review_payload={"summary": {"full_model_test_accuracy": 0.55, "most_useful_block_by_hotspot_impact": "price_confirmation", "ready_for_phase_check_next": True}},
    )

    assert result.summary["attribution_review_present"] is True
    assert result.summary["allow_model_deployment_now"] is False
