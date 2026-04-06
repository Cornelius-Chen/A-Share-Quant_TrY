from pathlib import Path

from a_share_quant.strategy.v133e_commercial_aerospace_cde_intraday_execution_governance_triage_v1 import (
    V133ECommercialAerospaceCDEIntradayExecutionGovernanceTriageAnalyzer,
)


def test_v133e_intraday_execution_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133ECommercialAerospaceCDEIntradayExecutionGovernanceTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "freeze_commercial_aerospace_intraday_execution_lane_until_protocol_unblocks"
    assert report.triage_rows[0]["status"] == "freeze_until_protocol_unblocks"
