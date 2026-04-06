from pathlib import Path

from a_share_quant.strategy.v133y_commercial_aerospace_point_in_time_all_session_feed_v1 import (
    V133YCommercialAerospacePointInTimeAllSessionFeedAnalyzer,
)


def test_v133y_commercial_aerospace_point_in_time_all_session_feed_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133YCommercialAerospacePointInTimeAllSessionFeedAnalyzer(repo_root).analyze()

    assert report.summary["seed_symbol_count"] == 6
    assert report.summary["all_session_count"] == 612
    assert report.summary["lineage_null_count"] == 0
