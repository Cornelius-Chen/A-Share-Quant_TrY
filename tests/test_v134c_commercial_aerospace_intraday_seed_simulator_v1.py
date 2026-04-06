from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134c_commercial_aerospace_intraday_seed_simulator_v1 import (
    V134CCommercialAerospaceIntradaySeedSimulatorAnalyzer,
)


def test_v134c_intraday_seed_simulator() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CCommercialAerospaceIntradaySeedSimulatorAnalyzer(repo_root).analyze()

    assert result.summary["seed_session_count"] == 6
    assert result.summary["simulated_order_count"] == len(result.order_rows)
    assert result.summary["simulated_order_count"] == 8
    assert result.summary["mild_watch_count"] == 5
    assert result.summary["severe_execution_count"] == 3
    assert result.summary["reversal_execution_count"] == 5
    assert result.summary["pending_out_of_window_count"] == 0
    assert all(
        int(row["fill_minute"]) == int(row["trigger_minute"]) + 1
        for row in result.order_rows
    )
    assert [row for row in result.order_rows if row["symbol"] == "601698"] == [
        row for row in result.order_rows if row["symbol"] == "601698" and row["trigger_tier"] == "severe_override_positive"
    ]
