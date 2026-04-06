from pathlib import Path

from a_share_quant.strategy.v130c_bk0480_aerospace_aviation_feed_harmonization_support_audit_v1 import (
    V130CBK0480AerospaceAviationFeedHarmonizationSupportAuditAnalyzer,
)


def test_v130c_bk0480_aerospace_aviation_feed_harmonization_support_audit_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130CBK0480AerospaceAviationFeedHarmonizationSupportAuditAnalyzer(repo_root).analyze()

    rows = {row["symbol"]: row["harmonization_status"] for row in result.candidate_rows}
    assert result.summary["same_plane_support_count"] == 0
    assert rows["600760"] == "historical_bridge_only"
    assert rows["002273"] == "timeline_only"
