from pathlib import Path

from a_share_quant.strategy.v127v_commercial_aerospace_uvw_window_derisk_triage_v1 import (
    V127VCommercialAerospaceUVWWindowDeriskTriageAnalyzer,
)


def test_v127v_window_derisk_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V127VCommercialAerospaceUVWWindowDeriskTriageAnalyzer(repo_root).analyze()

    assert report.summary["reference_variant"] == "veto_drag_trio_impulse_only"
