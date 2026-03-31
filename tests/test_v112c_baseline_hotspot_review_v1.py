from __future__ import annotations

from a_share_quant.strategy.v112c_baseline_hotspot_review_v1 import (
    V112CBaselineHotspotReviewAnalyzer,
)


def test_v112c_hotspot_review_extracts_primary_reading() -> None:
    result = V112CBaselineHotspotReviewAnalyzer().analyze(
        phase_charter_payload={"summary": {"ready_for_hotspot_review_next": True}},
        baseline_readout_payload={
            "fold_rows": [
                {"symbol": "300308", "stage": "major_markup", "predicted_label": "carry_constructive", "true_label": "failed", "correct": False},
                {"symbol": "300308", "stage": "major_markup", "predicted_label": "carry_constructive", "true_label": "failed", "correct": False},
                {"symbol": "300502", "stage": "high_level_consolidation", "predicted_label": "watch_constructive", "true_label": "failed", "correct": False},
                {"symbol": "300394", "stage": "deep_box_reset", "predicted_label": "failed", "true_label": "failed", "correct": True},
            ]
        },
    )

    assert result.summary["ready_for_sidecar_protocol_next"] is True
    assert result.top_error_rows[0]["stage"] == "major_markup"
