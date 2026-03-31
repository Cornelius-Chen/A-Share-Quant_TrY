from __future__ import annotations

from a_share_quant.strategy.v112_training_protocol_v1 import V112TrainingProtocolAnalyzer


def test_v112_training_protocol_freezes_feature_blocks_and_labels() -> None:
    result = V112TrainingProtocolAnalyzer().analyze(
        pilot_cycle_selection_payload={"summary": {"ready_for_training_protocol_next": True}},
    )

    assert result.summary["feature_block_count"] == 4
    assert result.summary["label_count"] == 3
    assert result.summary["ready_for_phase_check_next"] is True
