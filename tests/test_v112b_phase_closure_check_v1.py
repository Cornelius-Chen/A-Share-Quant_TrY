from __future__ import annotations

from a_share_quant.strategy.v112b_phase_closure_check_v1 import (
    V112BPhaseClosureCheckAnalyzer,
)


def test_v112b_phase_closure_keeps_training_blocked() -> None:
    result = V112BPhaseClosureCheckAnalyzer().analyze(
        phase_check_payload={
            "summary": {
                "dataset_frozen": True,
                "baseline_readout_present": True,
                "allow_strategy_training_now": False,
                "ready_for_phase_closure_next": True,
            }
        }
    )

    assert result.summary["v112b_success_criteria_met"] is True
    assert result.summary["enter_v112b_waiting_state_now"] is True
    assert result.summary["allow_auto_training_now"] is False
