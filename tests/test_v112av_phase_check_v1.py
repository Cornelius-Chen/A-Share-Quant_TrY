from pathlib import Path

from a_share_quant.strategy.v112av_phase_charter_v1 import load_json_report
from a_share_quant.strategy.v112av_phase_check_v1 import V112AVPhaseCheckAnalyzer


def test_v112av_phase_check_keeps_formal_rights_closed() -> None:
    analyzer = V112AVPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112av_phase_charter_v1.json")),
        patch_payload=load_json_report(Path("reports/analysis/v112av_cpo_branch_role_geometry_patch_pilot_v1.json")),
    )
    assert result.summary["allow_formal_training_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
