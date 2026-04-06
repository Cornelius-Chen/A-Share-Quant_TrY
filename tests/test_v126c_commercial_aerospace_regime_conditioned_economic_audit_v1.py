from pathlib import Path

from a_share_quant.strategy.v126c_commercial_aerospace_regime_conditioned_economic_audit_v1 import (
    V126CCommercialAerospaceRegimeConditionedEconomicAuditAnalyzer,
)


def test_v126c_runs_regime_conditioned_economic_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V126CCommercialAerospaceRegimeConditionedEconomicAuditAnalyzer(repo_root).analyze()
    assert result.summary["test_row_count"] > 0
