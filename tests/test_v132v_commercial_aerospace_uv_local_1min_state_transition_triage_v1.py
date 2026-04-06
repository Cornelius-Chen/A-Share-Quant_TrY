from pathlib import Path

from a_share_quant.strategy.v132v_commercial_aerospace_uv_local_1min_state_transition_triage_v1 import (
    V132VCommercialAerospaceUVLocal1MinStateTransitionTriageAnalyzer,
)


def test_v132v_local_1min_state_transition_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V132VCommercialAerospaceUVLocal1MinStateTransitionTriageAnalyzer(repo_root).analyze()

    assert report.summary["top_transition_pattern"] != ""
    assert report.triage_rows[1]["status"] == "retain_unchanged"
