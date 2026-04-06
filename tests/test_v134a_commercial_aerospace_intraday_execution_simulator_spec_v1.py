from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134a_commercial_aerospace_intraday_execution_simulator_spec_v1 import (
    V134ACommercialAerospaceIntradayExecutionSimulatorSpecAnalyzer,
)


def test_v134a_intraday_execution_simulator_spec() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ACommercialAerospaceIntradayExecutionSimulatorSpecAnalyzer(repo_root).analyze()

    assert result.summary["simulator_component_count"] == 6
    assert result.summary["action_mapping_count"] == 3
    assert result.summary["cost_item_count"] == 4
    assert result.summary["acceptance_item_count"] == 5
    assert result.summary["phase_1_status"] == "complete_phase_1_visibility_and_keep_intraday_execution_lane_blocked"
    assert all(row["ladder_consistency"] for row in result.action_rows)
    assert result.action_rows[0]["fill_ts"] == "open_t_plus_1"
    assert result.action_rows[1]["position_effect"] == "sell_50_percent_of_remaining_position"
    assert result.action_rows[2]["fill_ts"] == "no_immediate_trade"
