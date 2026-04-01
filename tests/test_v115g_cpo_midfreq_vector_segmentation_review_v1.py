from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v115g_cpo_midfreq_vector_segmentation_review_v1 import (
    V115GCpoMidfreqVectorSegmentationReviewAnalyzer,
)


def test_v115g_vector_segmentation() -> None:
    analyzer = V115GCpoMidfreqVectorSegmentationReviewAnalyzer(repo_root=Path("."))
    enriched_rows = [
        {
            "action_context": "add_vs_hold",
            "f30_breakout_efficiency": "0.7",
            "f60_breakout_efficiency": "0.8",
            "f30_close_vs_vwap": "0.02",
            "f60_close_vs_vwap": "0.03",
            "f30_close_location": "0.8",
            "f60_close_location": "0.85",
            "f30_pullback_from_high": "-0.02",
            "f60_pullback_from_high": "-0.01",
            "f30_afternoon_return": "0.03",
            "f60_afternoon_return": "0.04",
            "f30_high_time_ratio": "0.7",
            "f60_high_time_ratio": "0.8",
            "f30_failed_push_proxy": "0",
            "f60_failed_push_proxy": "0",
        },
        {
            "action_context": "reduce_vs_hold",
            "f30_breakout_efficiency": "0.1",
            "f60_breakout_efficiency": "0.2",
            "f30_close_vs_vwap": "-0.03",
            "f60_close_vs_vwap": "-0.02",
            "f30_close_location": "0.2",
            "f60_close_location": "0.25",
            "f30_pullback_from_high": "-0.07",
            "f60_pullback_from_high": "-0.08",
            "f30_afternoon_return": "-0.03",
            "f60_afternoon_return": "-0.02",
            "f30_high_time_ratio": "0.2",
            "f60_high_time_ratio": "0.3",
            "f30_failed_push_proxy": "1",
            "f60_failed_push_proxy": "1",
        },
        {
            "action_context": "close_vs_hold",
            "f30_breakout_efficiency": "0.15",
            "f60_breakout_efficiency": "0.25",
            "f30_close_vs_vwap": "-0.04",
            "f60_close_vs_vwap": "-0.05",
            "f30_close_location": "0.1",
            "f60_close_location": "0.15",
            "f30_pullback_from_high": "-0.09",
            "f60_pullback_from_high": "-0.10",
            "f30_afternoon_return": "-0.04",
            "f60_afternoon_return": "-0.05",
            "f30_high_time_ratio": "0.15",
            "f60_high_time_ratio": "0.2",
            "f30_failed_push_proxy": "1",
            "f60_failed_push_proxy": "1",
        },
    ]
    report, segmented = analyzer.analyze(enriched_rows=enriched_rows)

    assert report.summary["acceptance_posture"] == "freeze_v115g_cpo_midfreq_vector_segmentation_review_v1"
    assert report.summary["vector_count"] == 4
    assert len(segmented) == 3
    assert "breakout_quality_vector" in segmented[0]
    assert any(row["action_context"] == "add_vs_hold" for row in report.context_separation_rows)
