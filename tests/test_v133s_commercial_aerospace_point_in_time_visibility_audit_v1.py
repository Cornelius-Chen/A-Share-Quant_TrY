from pathlib import Path

from a_share_quant.strategy.v133s_commercial_aerospace_point_in_time_visibility_audit_v1 import (
    V133SCommercialAerospacePointInTimeVisibilityAuditAnalyzer,
)


def test_v133s_commercial_aerospace_point_in_time_visibility_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133SCommercialAerospacePointInTimeVisibilityAuditAnalyzer(repo_root).analyze()

    assert report.summary["same_bar_violation_count"] == 0
    assert report.summary["path_cutoff_violation_count"] == 0
    assert report.summary["lineage_monotonic_violation_count"] == 0
    assert report.summary["event_visibility_violation_count"] == 0
    assert report.summary["warmup_nonnull_violation_count"] == 0
