from pathlib import Path

from a_share_quant.strategy.v133t_commercial_aerospace_st_visibility_audit_triage_v1 import (
    V133TCommercialAerospaceSTVisibilityAuditTriageAnalyzer,
)


def test_v133t_commercial_aerospace_st_visibility_audit_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133TCommercialAerospaceSTVisibilityAuditTriageAnalyzer(repo_root).analyze()

    assert report.triage_rows[0]["status"] == "accepted_for_phase_1_extension"
    assert report.triage_rows[1]["status"] == "next_allowed_move"
    assert report.triage_rows[2]["status"] == "still_blocked"
