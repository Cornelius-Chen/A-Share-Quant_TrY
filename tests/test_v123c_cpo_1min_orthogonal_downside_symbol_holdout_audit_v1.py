from pathlib import Path

from a_share_quant.strategy.v123a_cpo_1min_orthogonal_downside_scan_v1 import write_report as write_v123a
from a_share_quant.strategy.v123a_cpo_1min_orthogonal_downside_scan_v1 import (
    V123ACpo1MinOrthogonalDownsideScanAnalyzer,
)
from a_share_quant.strategy.v123c_cpo_1min_orthogonal_downside_symbol_holdout_audit_v1 import (
    V123CCpo1MinOrthogonalDownsideSymbolHoldoutAuditAnalyzer,
)


def test_v123c_symbol_holdout_stays_above_random() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    write_v123a(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123a_cpo_1min_orthogonal_downside_scan_v1",
        result=V123ACpo1MinOrthogonalDownsideScanAnalyzer(repo_root=repo_root).analyze(),
    )
    result = V123CCpo1MinOrthogonalDownsideSymbolHoldoutAuditAnalyzer(repo_root=repo_root).analyze()
    assert result.summary["chosen_score_name"] == "gap_exhaustion_stall_score"
    assert result.summary["mean_test_balanced_accuracy"] > 0.53
    assert result.summary["min_test_balanced_accuracy"] > 0.52
