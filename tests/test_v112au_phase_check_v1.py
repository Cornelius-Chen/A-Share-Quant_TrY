from pathlib import Path

from a_share_quant.strategy.v112au_phase_charter_v1 import load_json_report
from a_share_quant.strategy.v112au_phase_check_v1 import V112AUPhaseCheckAnalyzer


def test_v112au_phase_check_keeps_formal_rights_closed() -> None:
    analyzer = V112AUPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112au_phase_charter_v1.json")),
        widen_payload=load_json_report(Path("reports/analysis/v112au_cpo_bounded_row_geometry_widen_pilot_v1.json")),
    )
    assert result.summary["allow_formal_training_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
