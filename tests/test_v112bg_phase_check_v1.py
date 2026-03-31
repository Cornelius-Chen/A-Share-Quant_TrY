from pathlib import Path

from a_share_quant.strategy.v112bg_phase_check_v1 import (
    V112BGPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bg_phase_check_marks_ready_for_closure() -> None:
    analyzer = V112BGPhaseCheckAnalyzer()
    result = analyzer.analyze(
        gap_review_payload=load_json_report(Path("reports/analysis/v112bg_cpo_oracle_vs_no_leak_gap_review_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
