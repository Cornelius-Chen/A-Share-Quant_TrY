from pathlib import Path

from a_share_quant.strategy.v113d_phase_charter_v1 import (
    V113DPhaseCharterAnalyzer,
    load_json_report,
)


def test_v113d_phase_charter_v1_opens_bounded_archetype_usage_pass() -> None:
    result = V113DPhaseCharterAnalyzer().analyze(
        prior_phase_payload=load_json_report(Path("reports/analysis/v113c_phase_closure_check_v1.json"))
    )
    assert result.summary["acceptance_posture"] == "open_v113d_bounded_archetype_usage_pass_v1"
    assert result.summary["ready_for_archetype_usage_pass_next"] is True
