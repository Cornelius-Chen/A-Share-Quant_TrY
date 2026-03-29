from __future__ import annotations

from a_share_quant.strategy.baseline_capture_diagnostic import BaselineCaptureDiagnostic


def test_baseline_capture_diagnostic_summarizes_strategy_slice_and_window_gaps() -> None:
    comparison_payload = {
        "comparisons": [
            {
                "dataset_name": "baseline",
                "candidate_name": "shared_default",
                "strategy_name": "a",
                "summary": {
                    "mainline_capture_ratio": 0.4,
                    "total_return": 0.02,
                    "missed_mainline_count": 3,
                },
                "window_breakdown": [
                    {
                        "window_id": "w1",
                        "symbol": "AAA",
                        "start_date": "2024-01-01",
                        "end_date": "2024-01-05",
                        "capturable_return": 0.1,
                        "capture_ratio": 0.8,
                    }
                ],
            },
            {
                "dataset_name": "baseline",
                "candidate_name": "balanced_compromise",
                "strategy_name": "a",
                "summary": {
                    "mainline_capture_ratio": 0.3,
                    "total_return": 0.03,
                    "missed_mainline_count": 4,
                },
                "window_breakdown": [
                    {
                        "window_id": "w1",
                        "symbol": "AAA",
                        "start_date": "2024-01-01",
                        "end_date": "2024-01-05",
                        "capturable_return": 0.1,
                        "capture_ratio": 0.2,
                    }
                ],
            },
        ]
    }
    slice_payload = {
        "comparisons": [
            {
                "dataset_name": "baseline",
                "slice_name": "q1",
                "candidate_name": "shared_default",
                "strategy_name": "a",
                "summary": {"mainline_capture_ratio": 0.4},
            },
            {
                "dataset_name": "baseline",
                "slice_name": "q1",
                "candidate_name": "balanced_compromise",
                "strategy_name": "a",
                "summary": {"mainline_capture_ratio": 0.25},
            },
        ]
    }

    result = BaselineCaptureDiagnostic().analyze(
        comparison_payload=comparison_payload,
        slice_payload=slice_payload,
        incumbent_name="shared_default",
        challenger_name="balanced_compromise",
        dataset_name="baseline",
    )

    assert result.summary["mean_capture_regression"] == 0.1
    assert result.strategy_deltas[0]["strategy_name"] == "a"
    assert result.strategy_deltas[0]["capture_regression"] == 0.1
    assert result.slice_deltas[0]["slice_name"] == "q1"
    assert result.slice_deltas[0]["capture_regression"] == 0.15
    assert result.top_window_regressions[0]["window_id"] == "w1"
    assert result.top_window_regressions[0]["capture_regression"] == 0.6
