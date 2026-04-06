from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135aw_commercial_aerospace_window_supply_chain_seed_audit_v1 import (
    V135AWCommercialAerospaceWindowSupplyChainSeedAuditV1Analyzer,
)


def test_v135aw_supply_chain_seed_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AWCommercialAerospaceWindowSupplyChainSeedAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 5
    assert result.summary["covered_window_count"] == 1
    assert result.summary["positive_support_sample_ready_count"] == 1
    assert result.summary["tradable_now_count"] == 1
    assert result.summary["watch_only_count"] == 4

