from pathlib import Path

from a_share_quant.strategy.v121t_cpo_recent_1min_bootstrap_v1 import (
    V121TCpoRecent1MinBootstrapAnalyzer,
)


def test_v121t_recent_1min_bootstrap_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V121TCpoRecent1MinBootstrapAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    assert result.summary["symbol_count"] == 4
    assert result.summary["total_row_count"] > 0
