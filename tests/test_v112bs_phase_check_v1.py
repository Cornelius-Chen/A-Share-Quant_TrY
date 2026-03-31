from pathlib import Path

from a_share_quant.strategy.v112bs_phase_check_v1 import (
    V112BSPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bs_phase_check_runs() -> None:
    analyzer = V112BSPhaseCheckAnalyzer()
    result = analyzer.analyze(
        refinement_payload=load_json_report(Path("reports/analysis/v112bs_penalized_target_mapping_refinement_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
