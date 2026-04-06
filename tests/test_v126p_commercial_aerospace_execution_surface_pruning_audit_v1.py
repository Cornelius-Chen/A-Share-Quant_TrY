from pathlib import Path

from a_share_quant.strategy.v126p_commercial_aerospace_execution_surface_pruning_audit_v1 import (
    V126PCommercialAerospaceExecutionSurfacePruningAuditAnalyzer,
)


def test_v126p_execution_surface_pruning_audit_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126PCommercialAerospaceExecutionSurfacePruningAuditAnalyzer(repo_root).analyze()
    assert result.summary["best_variant_executed_order_count"] >= 0
    assert result.summary["best_variant_final_equity"] > 0
