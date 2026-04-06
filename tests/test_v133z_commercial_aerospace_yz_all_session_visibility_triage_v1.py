from pathlib import Path

from a_share_quant.strategy.v133z_commercial_aerospace_yz_all_session_visibility_triage_v1 import (
    V133ZCommercialAerospaceYZAllSessionVisibilityTriageAnalyzer,
)


def test_v133z_commercial_aerospace_yz_all_session_visibility_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133ZCommercialAerospaceYZAllSessionVisibilityTriageAnalyzer(repo_root).analyze()

    assert report.triage_rows[0]["status"] == "retain_as_phase_1_terminal_surface"
    assert report.triage_rows[1]["status"] == "complete"
    assert report.triage_rows[2]["status"] == "still_blocked"
