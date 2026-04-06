from pathlib import Path

from a_share_quant.strategy.v133o_commercial_aerospace_point_in_time_visibility_spec_v1 import (
    V133OCommercialAerospacePointInTimeVisibilitySpecAnalyzer,
)


def test_v133o_commercial_aerospace_point_in_time_visibility_spec_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V133OCommercialAerospacePointInTimeVisibilitySpecAnalyzer(repo_root).analyze()

    assert report.summary["feed_column_count"] >= 10
    assert report.summary["seed_session_count"] == 6
    assert any(row["semantic_rule"] == "first_visible_ts_required" for row in report.semantics_rows)
    assert any(row["acceptance_item"] == "same_bar_no_peek" for row in report.acceptance_rows)
