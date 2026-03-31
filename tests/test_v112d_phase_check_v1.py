from __future__ import annotations

from a_share_quant.strategy.v112d_phase_check_v1 import V112DPhaseCheckAnalyzer


def test_v112d_phase_check_stays_report_only() -> None:
    result = V112DPhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112d_now": True}},
        sidecar_pilot_payload={"summary": {"model_count": 2, "best_model_name": "x", "baseline_test_accuracy": 0.4, "best_model_test_accuracy": 0.5, "ready_for_phase_check_next": True}},
    )

    assert result.summary["sidecar_pilot_present"] is True
    assert result.summary["allow_sidecar_deployment_now"] is False
