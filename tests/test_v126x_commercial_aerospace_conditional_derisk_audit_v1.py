from pathlib import Path

from a_share_quant.strategy.v126x_commercial_aerospace_conditional_derisk_audit_v1 import (
    V126XCommercialAerospaceConditionalDeriskAuditAnalyzer,
)


def test_v126x_conditional_derisk_audit_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126XCommercialAerospaceConditionalDeriskAuditAnalyzer(repo_root).analyze()
    assert result.summary["best_variant_final_equity"] > 0
