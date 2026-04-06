from pathlib import Path

from a_share_quant.strategy.v123u_cpo_drawdown_risk_layer_attribution_matrix_v1 import (
    V123UCpoDrawdownRiskLayerAttributionMatrixAnalyzer,
)


def test_v123u_drawdown_risk_layer_matrix_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V123UCpoDrawdownRiskLayerAttributionMatrixAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["interval_count"] == 3
    assert result.summary["heat_dominated_interval_count"] == 2
    assert result.summary["residual_dominated_interval_count"] == 1
