from pathlib import Path

from a_share_quant.strategy.v133v_commercial_aerospace_uv_broader_visibility_direction_triage_v1 import (
    V133VCommercialAerospaceUVBroaderVisibilityDirectionTriageAnalyzer,
)


def test_v133v_commercial_aerospace_uv_broader_visibility_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133VCommercialAerospaceUVBroaderVisibilityDirectionTriageAnalyzer(repo_root).analyze()

    assert report.summary["broader_hit_session_count"] == 24
    assert report.triage_rows[0]["status"] == "retain_as_phase_1_extension_surface"
    assert report.triage_rows[2]["status"] == "still_blocked"
