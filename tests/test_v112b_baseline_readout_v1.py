from __future__ import annotations

import pandas as pd

from a_share_quant.strategy.v112b_baseline_readout_v1 import (
    V112BBaselineReadoutAnalyzer,
)


def _mock_bars(start: str, periods: int, slope: float) -> pd.DataFrame:
    dates = pd.bdate_range(start=start, periods=periods)
    base = pd.Series(range(periods), dtype=float)
    close = 100.0 + base * slope + (base % 7) * 0.2
    open_ = close - 0.5
    high = close + 1.0
    low = close - 1.0
    volume = 1_000_000 + (base * 1_000.0)
    return pd.DataFrame(
        {
            "date": dates,
            "open": open_.astype(float),
            "close": close.astype(float),
            "high": high.astype(float),
            "low": low.astype(float),
            "volume": volume.astype(float),
        }
    )


def test_v112b_baseline_readout_runs_report_only_time_split() -> None:
    analyzer = V112BBaselineReadoutAnalyzer()
    result = analyzer.analyze(
        pilot_dataset_payload={
            "dataset_rows": [
                {
                    "symbol": "300308",
                    "name": "中际旭创",
                    "final_role_label_cn": "龙头/核心受益股",
                    "cycle_window": {
                        "first_markup_start": "2023-02",
                        "first_markup_end": "2023-06",
                        "cooling_and_box_start": "2023-07",
                        "cooling_and_box_end": "2024-01",
                        "major_markup_start": "2024-02",
                        "major_markup_end": "2024-05",
                    },
                },
                {
                    "symbol": "300502",
                    "name": "新易盛",
                    "final_role_label_cn": "高弹性核心受益股",
                    "cycle_window": {
                        "first_markup_start": "2023-02",
                        "first_markup_end": "2023-05",
                        "long_box_reset_start": "2023-06",
                        "long_box_reset_end": "2024-01",
                        "major_markup_start": "2024-02",
                        "major_markup_end": "2024-05",
                    },
                },
                {
                    "symbol": "300394",
                    "name": "天孚通信",
                    "final_role_label_cn": "上游核心器件平台受益股",
                    "cycle_window": {
                        "first_markup_start": "2023-02",
                        "first_markup_end": "2023-06",
                        "deep_box_reset_start": "2023-07",
                        "deep_box_reset_end": "2024-01",
                        "major_markup_start": "2024-02",
                        "major_markup_end": "2024-05",
                    },
                },
            ]
        },
        training_protocol_payload={"summary": {"acceptance_posture": "freeze_v112_training_protocol_v1"}},
        bar_frames_by_symbol={
            "300308": _mock_bars("2023-01-02", 420, 0.25),
            "300502": _mock_bars("2023-01-02", 420, 0.22),
            "300394": _mock_bars("2023-01-02", 420, 0.18),
        },
    )

    assert result.summary["sample_count"] > 50
    assert result.summary["allow_strategy_training_now"] is False
    assert result.summary["ready_for_phase_check_next"] is True
    assert len(result.fold_rows) == result.summary["test_count"]
