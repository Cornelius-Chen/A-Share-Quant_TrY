from pathlib import Path

from a_share_quant.strategy.v132r_commercial_aerospace_qr_governance_stack_triage_v1 import (
    V132RCommercialAerospaceQRGovernanceStackTriageAnalyzer,
)


def test_v132r_governance_stack_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V132RCommercialAerospaceQRGovernanceStackTriageAnalyzer(repo_root).analyze()

    assert report.summary["current_primary_variant"] == "tail_weakdrift_full"
    assert report.triage_rows[1]["status"] == "retain_unchanged"
