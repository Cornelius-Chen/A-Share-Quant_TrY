from pathlib import Path

from a_share_quant.strategy.v112ax_phase_check_v1 import (
    V112AXPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112ax_phase_check_keeps_formal_training_closed() -> None:
    analyzer = V112AXPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ax_phase_charter_v1.json")),
        pilot_payload=load_json_report(Path("reports/analysis/v112ax_cpo_guarded_branch_admitted_pilot_v1.json")),
    )
    assert result.summary["formal_training_now"] is False
