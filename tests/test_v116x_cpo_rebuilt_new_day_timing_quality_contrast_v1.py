from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v116x_cpo_rebuilt_new_day_timing_quality_contrast_v1 import (
    V116XCpoRebuiltNewDayTimingQualityContrastAnalyzer,
)


def test_v116x_rebuilt_new_day_contrast() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V116XCpoRebuiltNewDayTimingQualityContrastAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v116u_payload=json.loads((repo_root / "reports" / "analysis" / "v116u_cpo_expanded_window_action_timepoint_rebuild_v1.json").read_text(encoding="utf-8")),
        v116w_payload=json.loads((repo_root / "reports" / "analysis" / "v116w_cpo_corrected_cooled_shadow_expanded_window_validation_rebuilt_base_v1.json").read_text(encoding="utf-8")),
    )

    row_map = {row["signal_trade_date"]: row for row in result.contrast_rows}
    assert result.summary["authoritative_current_problem"] == "quality_discrimination_after_coverage_repair"
    assert result.summary["corrected_cooled_new_hit_day_count"] == 1
    assert row_map["2024-01-18"]["corrected_cooled_hit"] is True
    assert row_map["2023-11-07"]["all_late_only"] is True
    assert row_map["2024-01-23"]["diagnosis"] == "late_only_and_quality_weak"
