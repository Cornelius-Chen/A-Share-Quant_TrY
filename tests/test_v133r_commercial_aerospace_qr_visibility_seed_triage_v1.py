from pathlib import Path

from a_share_quant.strategy.v133r_commercial_aerospace_qr_visibility_seed_triage_v1 import (
    V133RCommercialAerospaceQRVisibilitySeedTriageAnalyzer,
)


def test_v133r_commercial_aerospace_qr_visibility_seed_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133RCommercialAerospaceQRVisibilitySeedTriageAnalyzer(repo_root).analyze()

    assert report.summary["seed_session_count"] == 6
    assert report.triage_rows[0]["status"] == "retain_as_phase_1_seed_surface"
    assert report.triage_rows[2]["status"] == "blocked_until_visibility_seed_surface_is_accepted"
