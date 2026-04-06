from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ax_commercial_aerospace_aw_window_supply_chain_direction_triage_v1 import (
    V135AXCommercialAerospaceAWWindowSupplyChainDirectionTriageV1Analyzer,
)


def test_v135ax_supply_chain_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AXCommercialAerospaceAWWindowSupplyChainDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["window_count"] == 1
    assert result.summary["positive_support_ready_count"] == 1
    assert result.triage_rows[0]["sample_window_id"] == "ca_train_window_001"
    assert "positive_support_training" in result.triage_rows[0]["recommendation"]
