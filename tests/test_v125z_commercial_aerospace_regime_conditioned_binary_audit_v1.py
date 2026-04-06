from pathlib import Path

from a_share_quant.strategy.v125z_commercial_aerospace_regime_conditioned_binary_audit_v1 import (
    V125ZCommercialAerospaceRegimeConditionedBinaryAuditAnalyzer,
)


def test_v125z_runs_regime_conditioned_binary_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125ZCommercialAerospaceRegimeConditionedBinaryAuditAnalyzer(repo_root).analyze()
    assert result.summary["task_count"] == 2
