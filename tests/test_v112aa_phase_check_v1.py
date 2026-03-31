from pathlib import Path

from a_share_quant.strategy.v112aa_phase_check_v1 import (
    V112AAPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112aa_phase_check_keeps_labeling_closed() -> None:
    analyzer = V112AAPhaseCheckAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112aa_phase_charter_v1.json")),
        cohort_map_payload=load_json_report(Path("reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json")),
    )
    assert result.summary["allow_auto_labeling_now"] is False
    assert result.summary["ready_for_phase_closure_next"] is True
