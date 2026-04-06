from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134g_commercial_aerospace_intraday_seed_simulator_deterministic_audit_v1 import (
    V134GCommercialAerospaceIntradaySeedSimulatorDeterministicAuditAnalyzer,
)


def test_v134g_seed_simulator_deterministic_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134GCommercialAerospaceIntradaySeedSimulatorDeterministicAuditAnalyzer(repo_root).analyze()

    assert result.summary["seed_session_with_orders_count"] == 6
    assert result.summary["double_run_exact_match"] is True
    assert result.summary["monotonic_fill_violation_count"] == 0
    assert result.summary["duplicate_fill_violation_count"] == 0
    assert result.summary["post_flat_action_violation_count"] == 0

