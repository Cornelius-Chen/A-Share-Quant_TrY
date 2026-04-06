from pathlib import Path

from a_share_quant.strategy.v124e_cpo_heat_plus_riskoff_add_suppression_audit_v1 import (
    V124ECpoHeatPlusRiskoffAddSuppressionAuditAnalyzer,
)


def test_v124e_add_suppression_variants_are_valid() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124ECpoHeatPlusRiskoffAddSuppressionAuditAnalyzer(repo_root=repo_root).analyze()

    assert result.summary["variant_count"] == 6
    rows = {row["variant_name"]: row for row in result.variant_rows}
    assert "balanced_heat_reference" in rows
    for row in rows.values():
        assert row["final_equity"] > 0
        assert 0.0 <= row["max_drawdown"] <= 1.0
