from pathlib import Path

from a_share_quant.strategy.v133q_commercial_aerospace_point_in_time_seed_feed_v1 import (
    V133QCommercialAerospacePointInTimeSeedFeedAnalyzer,
)


def test_v133q_commercial_aerospace_point_in_time_seed_feed_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133QCommercialAerospacePointInTimeSeedFeedAnalyzer(repo_root).analyze()

    assert report.summary["seed_session_count"] == 6
    assert report.summary["feed_row_count"] == 360
    assert report.summary["lineage_null_count"] == 0
    assert any(row["acceptance_item"] == "lineage_fields_non_null" and row["status"] == "pass" for row in report.acceptance_rows)
