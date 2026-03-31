from pathlib import Path

from a_share_quant.strategy.v112ac_phase_charter_v1 import (
    V112ACPhaseCharterAnalyzer,
    load_json_report,
)


def test_v112ac_phase_charter_opens_after_cohort_and_labeling_review() -> None:
    analyzer = V112ACPhaseCharterAnalyzer()
    result = analyzer.analyze(
        cohort_map_payload=load_json_report(Path("reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json")),
        labeling_review_payload=load_json_report(Path("reports/analysis/v112ab_cpo_bounded_labeling_review_v1.json")),
    )
    assert result.summary["do_open_v112ac_now"] is True
    assert result.charter["phase_name"] == "V1.12AC CPO Unsupervised Role-Challenge Probe"
