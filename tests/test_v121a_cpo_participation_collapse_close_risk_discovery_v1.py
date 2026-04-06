from pathlib import Path

from a_share_quant.strategy.v121a_cpo_participation_collapse_close_risk_discovery_v1 import (
    V121ACpoParticipationCollapseCloseRiskDiscoveryAnalyzer,
)


def test_v121a_close_risk_discovery_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121ACpoParticipationCollapseCloseRiskDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    assert result.summary["positive_close_row_count"] > 0
    assert result.summary["row_count"] > result.summary["positive_close_row_count"]

