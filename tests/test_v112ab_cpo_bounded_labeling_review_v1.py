from pathlib import Path

from a_share_quant.strategy.v112ab_cpo_bounded_labeling_review_v1 import (
    V112ABCPOBoundedLabelingReviewAnalyzer,
    load_json_report,
)


def test_v112ab_labeling_review_keeps_freeze_closed() -> None:
    analyzer = V112ABCPOBoundedLabelingReviewAnalyzer()
    result = analyzer.analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v112ab_phase_charter_v1.json")),
        cohort_map_payload=load_json_report(Path("reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json")),
    )
    assert result.summary["primary_labeling_surface_count"] == 3
    assert result.summary["secondary_labeling_surface_count"] == 4
    assert result.summary["formal_label_freeze_still_forbidden"] is True
