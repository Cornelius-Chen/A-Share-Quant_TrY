from pathlib import Path

from a_share_quant.strategy.v113a_phase_charter_v1 import V113APhaseCharterAnalyzer, load_json_report


def test_v113a_phase_charter_v1_opens_schema_phase() -> None:
    result = V113APhaseCharterAnalyzer().analyze(
        prior_phase_payload=load_json_report(Path("reports/analysis/v113_phase_closure_check_v1.json"))
    )
    assert result.summary["ready_for_schema_freeze_next"] is True
    assert "execution timing schema" in " ".join(result.out_of_scope)
