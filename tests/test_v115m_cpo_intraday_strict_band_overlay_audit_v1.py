from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.strategy.v115m_cpo_intraday_strict_band_overlay_audit_v1 import (
    V115MCpoIntradayStrictBandOverlayAuditAnalyzer,
)


def test_v115m_strict_band_overlay_audit_matches_expected_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115MCpoIntradayStrictBandOverlayAuditAnalyzer(repo_root=repo_root)
    report, _ = analyzer.analyze(
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
        v114x_payload=json.loads((repo_root / "reports" / "analysis" / "v114x_cpo_probability_expectancy_sizing_framework_repaired_v1.json").read_text(encoding="utf-8")),
        v115l_payload=json.loads((repo_root / "reports" / "analysis" / "v115l_cpo_intraday_strict_band_refinement_v1.json").read_text(encoding="utf-8")),
        band_rows=V115MCpoIntradayStrictBandOverlayAuditAnalyzer._load_band_rows(
            repo_root / "data" / "training" / "cpo_midfreq_band_action_audit_rows_v1.csv"
        ),
    )
    summary = report.summary

    assert summary["acceptance_posture"] == "freeze_v115m_cpo_intraday_strict_band_overlay_audit_v1"
    assert summary["strict_add_band_count"] >= 1
    assert summary["top_miss_day_count"] == 6
    assert summary["top_miss_add_row_count"] == 10
    assert summary["strict_hit_miss_day_count"] >= 1
    assert summary["strict_hit_miss_row_count"] >= 1
    assert 0.0 <= summary["strict_hit_rate_vs_top_miss_days"] <= 1.0
    assert 0.0 <= summary["strict_hit_rate_vs_top_miss_rows"] <= 1.0
    assert summary["strict_hit_expectancy_mean"] >= summary["all_top_miss_expectancy_mean"]
    assert summary["strict_hit_adverse_mean"] >= summary["all_top_miss_adverse_mean"]
    assert 0.0 <= summary["strict_add_leakage_into_entry_rate"] <= 1.0
    assert 0.0 <= summary["strict_add_leakage_into_close_rate"] <= 1.0
    assert summary["strict_add_leakage_into_reduce_rate"] == 0.0
    assert summary["candidate_only_overlay"] is True

    assert len(report.miss_day_uplift_rows) == summary["strict_hit_miss_day_count"]
    assert all(row["target_gross_exposure_floor_from_v114x"] >= 0.3 for row in report.miss_day_uplift_rows)
