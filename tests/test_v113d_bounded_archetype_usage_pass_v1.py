from pathlib import Path

from a_share_quant.strategy.v113d_bounded_archetype_usage_pass_v1 import (
    V113DBoundedArchetypeUsagePassAnalyzer,
    load_json_report,
)


def test_v113d_bounded_archetype_usage_pass_v1_keeps_template_promotion_closed() -> None:
    result = V113DBoundedArchetypeUsagePassAnalyzer().analyze(
        phase_charter_payload=load_json_report(Path("reports/analysis/v113d_phase_charter_v1.json")),
        template_entry_payload=load_json_report(Path("reports/analysis/v113_template_entry_v1.json")),
        state_usage_review_payload=load_json_report(Path("reports/analysis/v113c_bounded_state_usage_review_v1.json")),
    )
    assert result.summary["archetype_count_reviewed"] == 3
    assert result.summary["clean_template_review_asset_count"] == 1
    assert result.summary["formal_template_promotion_now"] is False
