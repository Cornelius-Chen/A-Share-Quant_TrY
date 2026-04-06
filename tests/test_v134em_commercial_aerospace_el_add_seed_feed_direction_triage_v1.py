from pathlib import Path

from a_share_quant.strategy.v134el_commercial_aerospace_intraday_add_point_in_time_seed_feed_v1 import (
    V134ELCommercialAerospaceIntradayAddPointInTimeSeedFeedV1Analyzer,
    write_report as write_feed_report,
)
from a_share_quant.strategy.v134em_commercial_aerospace_el_add_seed_feed_direction_triage_v1 import (
    V134EMCommercialAerospaceELAddSeedFeedDirectionTriageV1Analyzer,
)


def test_v134em_commercial_aerospace_el_add_seed_feed_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    feed = V134ELCommercialAerospaceIntradayAddPointInTimeSeedFeedV1Analyzer(repo_root).analyze()
    write_feed_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134el_commercial_aerospace_intraday_add_point_in_time_seed_feed_v1",
        result=feed,
    )
    result = V134EMCommercialAerospaceELAddSeedFeedDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_intraday_add_point_in_time_seed_feed_and_shift_next_to_add_tiered_label_specification"
    )
