from pathlib import Path

from a_share_quant.strategy.v133j_program_master_governance_triage_v1 import (
    V133JProgramMasterGovernanceTriageAnalyzer,
)


def test_v133j_program_master_governance_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133JProgramMasterGovernanceTriageAnalyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "freeze_program_lines_and_wait_for_explicit_gate_changes"
    assert report.triage_rows[1]["status"] == "blocked"
