from pathlib import Path

from a_share_quant.strategy.v133a_commercial_aerospace_intraday_governance_packaging_v1 import (
    V133ACommercialAerospaceIntradayGovernancePackagingAnalyzer,
)


def test_v133a_intraday_governance_packaging_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133ACommercialAerospaceIntradayGovernancePackagingAnalyzer(repo_root).analyze()

    assert report.summary["current_primary_variant"] == "tail_weakdrift_full"
    assert len(report.transferable_rows) >= 5
    assert len(report.execution_blocker_rows) == 3

