from pathlib import Path

from a_share_quant.strategy.v123y_cpo_heat_conditioned_riskoff_execution_audit_v1 import (
    V123YCpoHeatConditionedRiskoffExecutionAuditAnalyzer,
)


def test_v123y_heat_conditioned_riskoff_execution_variants_are_valid() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V123YCpoHeatConditionedRiskoffExecutionAuditAnalyzer(repo_root=repo_root).analyze()

    assert result.summary["variant_count"] == 6
    rows = {row["variant_name"]: row for row in result.variant_rows}
    assert "balanced_heat_reference" in rows
    assert rows["balanced_heat_reference"]["executed_reduce_count"] == 0
    assert rows["balanced_heat_reference"]["executed_add_count"] > 0
    for name, row in rows.items():
        assert row["final_equity"] > 0
        assert 0.0 <= row["max_drawdown"] <= 1.0
        if name != "balanced_heat_reference":
            assert row["suppressed_reduce_count"] >= 0
