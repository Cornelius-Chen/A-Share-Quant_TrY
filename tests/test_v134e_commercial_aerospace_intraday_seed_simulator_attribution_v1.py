from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134e_commercial_aerospace_intraday_seed_simulator_attribution_v1 import (
    V134ECommercialAerospaceIntradaySeedSimulatorAttributionAnalyzer,
)


def test_v134e_seed_simulator_attribution() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ECommercialAerospaceIntradaySeedSimulatorAttributionAnalyzer(repo_root).analyze()

    assert result.summary["order_count"] == 8
    assert result.summary["session_count"] == 6
    assert result.summary["same_day_loss_avoided_total"] > 0
    assert result.summary["top_tier_by_same_day_loss_avoided"] in {
        "reversal_watch",
        "severe_override_positive",
    }
    assert len(result.tier_rows) == 2

