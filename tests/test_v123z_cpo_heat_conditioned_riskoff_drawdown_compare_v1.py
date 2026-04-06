from pathlib import Path

from a_share_quant.strategy.v123y_cpo_heat_conditioned_riskoff_execution_audit_v1 import (
    V123YCpoHeatConditionedRiskoffExecutionAuditAnalyzer,
)
from a_share_quant.strategy.v123z_cpo_heat_conditioned_riskoff_drawdown_compare_v1 import (
    V123ZCpoHeatConditionedRiskoffDrawdownCompareAnalyzer,
)


def test_v123z_heat_conditioned_compare_references_existing_interval_map() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    V123YCpoHeatConditionedRiskoffExecutionAuditAnalyzer(repo_root=repo_root).analyze()
    result = V123ZCpoHeatConditionedRiskoffDrawdownCompareAnalyzer(repo_root=repo_root).analyze()

    assert len(result.drawdown_compare_rows) == 3
    assert result.summary["best_heat_conditioned_variant_name"]
    for row in result.drawdown_compare_rows:
        assert row["interval_rank"] in {1, 2, 3}
        assert row["best_heat_conditioned_full_curve_mdd"] >= 0.0
