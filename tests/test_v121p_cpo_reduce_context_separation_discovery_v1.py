from pathlib import Path

from a_share_quant.strategy.v121p_cpo_reduce_context_separation_discovery_v1 import (
    V121PCpoReduceContextSeparationDiscoveryAnalyzer,
)


def test_v121p_reduce_context_separation_discovery_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121PCpoReduceContextSeparationDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    assert result.summary["positive_reduce_row_count"] > 0
    assert result.summary["comparator_positive_row_count"] > result.summary["positive_reduce_row_count"]
