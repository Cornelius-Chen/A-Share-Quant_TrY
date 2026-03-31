from __future__ import annotations

import pandas as pd

from a_share_quant.strategy.v112g_baseline_readout_v2 import V112GBaselineReadoutV2Analyzer


def _mock_bars(start: str, periods: int, slope: float) -> pd.DataFrame:
    dates = pd.bdate_range(start=start, periods=periods)
    base = pd.Series(range(periods), dtype=float)
    close = 100.0 + base * slope + (base % 7) * 0.2
    return pd.DataFrame(
        {
            "date": dates,
            "open": (close - 0.5).astype(float),
            "close": close.astype(float),
            "high": (close + 1.0).astype(float),
            "low": (close - 1.0).astype(float),
            "volume": (1_000_000 + base * 1_000.0).astype(float),
        }
    )


def test_v112g_baseline_readout_v2_runs_same_dataset_rerun() -> None:
    analyzer = V112GBaselineReadoutV2Analyzer()
    result = analyzer.analyze(
        pilot_dataset_payload={
            "dataset_rows": [
                {"symbol": "300308", "cycle_window": {"first_markup_start": "2023-02", "first_markup_end": "2023-06", "cooling_and_box_start": "2023-07", "cooling_and_box_end": "2024-01", "major_markup_start": "2024-02", "major_markup_end": "2024-05"}},
                {"symbol": "300502", "cycle_window": {"first_markup_start": "2023-02", "first_markup_end": "2023-05", "long_box_reset_start": "2023-06", "long_box_reset_end": "2024-01", "major_markup_start": "2024-02", "major_markup_end": "2024-05"}},
                {"symbol": "300394", "cycle_window": {"first_markup_start": "2023-02", "first_markup_end": "2023-06", "deep_box_reset_start": "2023-07", "deep_box_reset_end": "2024-01", "major_markup_start": "2024-02", "major_markup_end": "2024-05"}},
            ]
        },
        training_protocol_payload={"summary": {"acceptance_posture": "freeze_v112_training_protocol_v1"}},
        baseline_v1_payload={"summary": {"test_accuracy": 0.4509}, "fold_rows": []},
        bar_frames_by_symbol={
            "300308": _mock_bars("2023-01-02", 420, 0.25),
            "300502": _mock_bars("2023-01-02", 420, 0.22),
            "300394": _mock_bars("2023-01-02", 420, 0.18),
        },
    )

    assert result.summary["feature_count_v2"] == 15
    assert result.summary["ready_for_gbdt_v2_next"] is True
