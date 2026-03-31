from pathlib import Path

from a_share_quant.strategy.v112bp_phase_check_v1 import (
    V112BPPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bp_phase_check_accepts_completed_fusion() -> None:
    analyzer = V112BPPhaseCheckAnalyzer()
    result = analyzer.analyze(
        fusion_pilot_payload=load_json_report(Path("reports/analysis/v112bp_cpo_selector_maturity_fusion_pilot_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
