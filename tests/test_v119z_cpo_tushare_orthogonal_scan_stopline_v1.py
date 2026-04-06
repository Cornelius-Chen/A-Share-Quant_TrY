from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v119z_cpo_tushare_orthogonal_scan_stopline_v1 import (
    V119ZCpoTushareOrthogonalScanStoplineAnalyzer,
)


def test_v119z_tushare_orthogonal_scan_stopline_runs() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V119ZCpoTushareOrthogonalScanStoplineAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["scan_candidate_count"] >= 5
    assert "orthogonal_scan_stopline_reached" in result.summary
