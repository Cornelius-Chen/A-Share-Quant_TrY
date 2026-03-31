from pathlib import Path

from a_share_quant.strategy.v112bk_phase_check_v1 import (
    V112BKPhaseCheckAnalyzer,
    load_json_report,
)


def test_v112bk_phase_check_accepts_tree_ranker_search() -> None:
    analyzer = V112BKPhaseCheckAnalyzer()
    result = analyzer.analyze(
        tree_ranker_search_payload=load_json_report(Path("reports/analysis/v112bk_cpo_tree_ranker_search_v1.json")),
    )
    assert result.summary["ready_for_phase_closure_next"] is True
