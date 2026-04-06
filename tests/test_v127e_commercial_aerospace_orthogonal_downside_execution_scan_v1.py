from pathlib import Path

from a_share_quant.strategy.v127e_commercial_aerospace_orthogonal_downside_execution_scan_v1 import (
    V127ECommercialAerospaceOrthogonalDownsideExecutionScanAnalyzer,
)


def test_v127e_orthogonal_downside_execution_scan_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V127ECommercialAerospaceOrthogonalDownsideExecutionScanAnalyzer(repo_root).analyze()
    assert len(result.variant_rows) == 3
