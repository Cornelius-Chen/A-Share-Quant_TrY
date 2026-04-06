from pathlib import Path

from a_share_quant.strategy.v133h_commercial_aerospace_fgh_intraday_reopen_governance_triage_v1 import (
    V133HCommercialAerospaceFGHIntradayReopenGovernanceTriageAnalyzer,
)


def test_v133h_intraday_reopen_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133HCommercialAerospaceFGHIntradayReopenGovernanceTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "freeze_commercial_aerospace_intraday_branch_and_wait_for_change_gate"
    assert report.triage_rows[0]["status"] == "freeze_and_wait_for_change_gate"
