from pathlib import Path

from a_share_quant.strategy.v123w_cpo_heat_plus_riskoff_integration_audit_v1 import (
    V123WCpoHeatPlusRiskoffIntegrationAuditAnalyzer,
)


def test_v123w_heat_plus_riskoff_integration_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V123WCpoHeatPlusRiskoffIntegrationAuditAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["variant_count"] == 8
    names = {row["variant_name"] for row in result.variant_rows}
    assert "balanced_heat_reference" in names
    assert any(row["executed_reduce_count"] > 0 for row in result.variant_rows if row["riskoff_quantile"] != "none")
