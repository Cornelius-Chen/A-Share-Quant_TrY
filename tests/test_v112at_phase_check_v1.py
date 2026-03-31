from pathlib import Path

from a_share_quant.strategy.v112at_phase_charter_v1 import load_json_report
from a_share_quant.strategy.v112at_phase_check_v1 import V112ATPhaseCheckAnalyzer


def test_v112at_phase_check_keeps_training_closed() -> None:
    analyzer = V112ATPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112at_phase_charter_v1.json")),
        rerun_payload=load_json_report(Path("reports/analysis/v112at_cpo_post_patch_rerun_v1.json")),
    )
    assert result.summary["allow_auto_training_now"] is False
    assert result.summary["allow_row_geometry_widen_now"] is True
    assert result.summary["ready_for_phase_closure_next"] is True
