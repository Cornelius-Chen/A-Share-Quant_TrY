from __future__ import annotations

from a_share_quant.strategy.v112c_sidecar_protocol_v1 import (
    V112CSidecarProtocolAnalyzer,
)


def test_v112c_sidecar_protocol_freezes_same_dataset_rule() -> None:
    result = V112CSidecarProtocolAnalyzer().analyze(
        hotspot_review_payload={"summary": {"ready_for_sidecar_protocol_next": True}},
        training_protocol_payload={"summary": {"acceptance_posture": "freeze_v112_training_protocol_v1"}},
    )

    assert result.summary["candidate_model_family_count"] == 2
    assert "same_dataset_rule" in result.protocol
    assert result.summary["ready_for_phase_check_next"] is True
