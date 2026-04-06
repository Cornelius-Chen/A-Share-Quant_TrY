from pathlib import Path

from a_share_quant.strategy.v121i_cpo_reduce_side_board_risk_off_discovery_v1 import (
    V121ICpoReduceSideBoardRiskOffDiscoveryAnalyzer,
)


def test_v121i_reduce_side_board_risk_off_discovery_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121ICpoReduceSideBoardRiskOffDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    assert result.summary["positive_reduce_row_count"] > 0
    assert result.summary["reduce_row_count"] > result.summary["positive_reduce_row_count"]
