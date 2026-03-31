from __future__ import annotations

from a_share_quant.strategy.v112b_phase_check_v1 import V112BPhaseCheckAnalyzer


def test_v112b_phase_check_requires_review_posture() -> None:
    result = V112BPhaseCheckAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112b_now": True}},
        pilot_dataset_freeze_payload={"summary": {"dataset_row_count": 3, "all_rows_owner_accepted": True, "ready_for_baseline_readout_next": True}},
        baseline_readout_payload={"summary": {"sample_count": 120, "test_accuracy": 0.6, "allow_strategy_training_now": False, "ready_for_phase_check_next": True}},
    )

    assert result.summary["dataset_frozen"] is True
    assert result.summary["baseline_readout_present"] is True
    assert result.summary["allow_strategy_training_now"] is False
