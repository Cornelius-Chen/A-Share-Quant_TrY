from pathlib import Path

from a_share_quant.strategy.v133u_commercial_aerospace_point_in_time_broader_hit_feed_v1 import (
    V133UCommercialAerospacePointInTimeBroaderHitFeedAnalyzer,
)


def test_v133u_commercial_aerospace_point_in_time_broader_hit_feed_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133UCommercialAerospacePointInTimeBroaderHitFeedAnalyzer(repo_root).analyze()

    assert report.summary["broader_hit_session_count"] == 24
    assert report.summary["feed_row_count"] == 1440
    assert report.summary["lineage_null_count"] == 0
