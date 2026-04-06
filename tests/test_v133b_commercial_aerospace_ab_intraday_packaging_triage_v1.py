from pathlib import Path

from a_share_quant.strategy.v133b_commercial_aerospace_ab_intraday_packaging_triage_v1 import (
    V133BCommercialAerospaceABIntradayPackagingTriageAnalyzer,
)


def test_v133b_intraday_packaging_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133BCommercialAerospaceABIntradayPackagingTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "freeze_commercial_aerospace_intraday_governance_package_and_stop_local_micro_tuning"
    assert report.triage_rows[1]["status"] == "blocked"
