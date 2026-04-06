from pathlib import Path

from a_share_quant.strategy.v123a_cpo_1min_orthogonal_downside_scan_v1 import (
    V123ACpo1MinOrthogonalDownsideScanAnalyzer,
)


def test_v123a_scan_selects_orthogonal_candidate() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V123ACpo1MinOrthogonalDownsideScanAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["scan_count"] == 3
    assert result.summary["chosen_score_name"] == "gap_exhaustion_stall_score"
    assert result.summary["chosen_corr_vs_downside_failure"] < 0.65
    assert result.summary["chosen_q75_balanced_accuracy"] > 0.53

