from pathlib import Path

from a_share_quant.strategy.v134el_commercial_aerospace_intraday_add_point_in_time_seed_feed_v1 import (
    V134ELCommercialAerospaceIntradayAddPointInTimeSeedFeedV1Analyzer,
)


def test_v134el_commercial_aerospace_intraday_add_point_in_time_seed_feed_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ELCommercialAerospaceIntradayAddPointInTimeSeedFeedV1Analyzer(repo_root).analyze()

    assert result.summary["seed_session_count"] == 55
    assert result.summary["feed_row_count"] == 3300
    assert result.summary["lineage_null_count"] == 0
