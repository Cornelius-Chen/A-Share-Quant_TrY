from pathlib import Path

from a_share_quant.strategy.v133x_commercial_aerospace_wx_broader_visibility_triage_v1 import (
    V133XCommercialAerospaceWXBroaderVisibilityTriageAnalyzer,
)


def test_v133x_commercial_aerospace_wx_broader_visibility_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133XCommercialAerospaceWXBroaderVisibilityTriageAnalyzer(repo_root).analyze()

    assert report.triage_rows[0]["status"] == "accepted_as_phase_1_broader_surface"
    assert report.triage_rows[1]["status"] == "next_allowed_move"
    assert report.triage_rows[2]["status"] == "still_blocked"
