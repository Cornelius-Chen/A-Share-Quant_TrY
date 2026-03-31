from pathlib import Path

from a_share_quant.strategy.v113_phase_charter_v1 import V113PhaseCharterAnalyzer, load_json_report


def test_v113_phase_charter_v1_reenters_higher_leverage_template_line() -> None:
    result = V113PhaseCharterAnalyzer().analyze(
        prior_phase_payload=load_json_report(Path("reports/analysis/v112n_phase_closure_check_v1.json"))
    )
    assert result.summary["ready_for_template_entry_next"] is True
    assert "execution timing logic" in " ".join(result.out_of_scope)
