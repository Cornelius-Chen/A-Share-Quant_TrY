from __future__ import annotations

from a_share_quant.strategy.drawdown_gap_analysis import DrawdownGapAnalyzer


def test_drawdown_gap_analyzer_identifies_weakest_dataset_strategy_and_slice() -> None:
    payload = {
        "source_report": "dummy.json",
        "comparisons": [
            {
                "dataset_name": "theme",
                "slice_name": "q1",
                "slice_start": "2024-01-01",
                "slice_end": "2024-03-31",
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_a",
                "summary": {
                    "total_return": 0.01,
                    "mainline_capture_ratio": 0.20,
                    "max_drawdown": 0.010,
                },
            },
            {
                "dataset_name": "theme",
                "slice_name": "q1",
                "slice_start": "2024-01-01",
                "slice_end": "2024-03-31",
                "candidate_name": "buffer_only_012",
                "strategy_name": "mainline_trend_a",
                "summary": {
                    "total_return": 0.009,
                    "mainline_capture_ratio": 0.19,
                    "max_drawdown": 0.012,
                },
            },
            {
                "dataset_name": "baseline",
                "slice_name": "q2",
                "slice_start": "2024-04-01",
                "slice_end": "2024-06-30",
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_b",
                "summary": {
                    "total_return": 0.005,
                    "mainline_capture_ratio": 0.10,
                    "max_drawdown": 0.020,
                },
            },
            {
                "dataset_name": "baseline",
                "slice_name": "q2",
                "slice_start": "2024-04-01",
                "slice_end": "2024-06-30",
                "candidate_name": "buffer_only_012",
                "strategy_name": "mainline_trend_b",
                "summary": {
                    "total_return": 0.007,
                    "mainline_capture_ratio": 0.12,
                    "max_drawdown": 0.017,
                },
            },
        ],
    }

    result = DrawdownGapAnalyzer().analyze(
        payload=payload,
        incumbent_name="shared_default",
        challenger_name="buffer_only_012",
    )

    assert result.summary["weakest_dataset_strategy"]["dataset_name"] == "theme"
    assert result.summary["weakest_dataset_strategy"]["strategy_name"] == "mainline_trend_a"
    assert result.summary["weakest_slice"]["dataset_name"] == "theme"
    assert result.summary["weakest_slice"]["slice_name"] == "q1"
    assert result.weakest_rows[0]["drawdown_improvement"] == -0.002
