from pathlib import Path

from a_share_quant.strategy.v123m_cpo_daily_residual_downside_discovery_v1 import (
    V123MCpoDailyResidualDownsideDiscoveryAnalyzer,
)


def test_v123m_daily_residual_downside_discovery_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V123MCpoDailyResidualDownsideDiscoveryAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["sample_row_count"] == 124
    assert result.summary["positive_row_count"] == 89
    assert result.summary["negative_row_count"] == 35
    assert result.summary["selected_q75_balanced_accuracy"] > 0.5
