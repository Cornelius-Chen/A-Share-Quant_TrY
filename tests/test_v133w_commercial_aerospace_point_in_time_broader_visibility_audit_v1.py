from pathlib import Path

from a_share_quant.strategy.v133w_commercial_aerospace_point_in_time_broader_visibility_audit_v1 import (
    V133WCommercialAerospacePointInTimeBroaderVisibilityAuditAnalyzer,
)


def test_v133w_commercial_aerospace_point_in_time_broader_visibility_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133WCommercialAerospacePointInTimeBroaderVisibilityAuditAnalyzer(repo_root).analyze()

    assert report.summary["broader_hit_session_count"] == 24
    assert report.summary["same_bar_violation_count"] == 0
    assert report.summary["path_cutoff_violation_count"] == 0
    assert report.summary["lineage_monotonic_violation_count"] == 0
    assert report.summary["event_visibility_violation_count"] == 0
    assert report.summary["warmup_nonnull_violation_count"] == 0
