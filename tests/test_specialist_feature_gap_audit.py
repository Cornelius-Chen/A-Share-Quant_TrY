from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.specialist_feature_gap_audit import SpecialistFeatureGapAuditAnalyzer


def test_specialist_feature_gap_audit_flags_cross_strategy_mixed_and_stacked() -> None:
    reports = [
        {
            "report_name": "mixed_b",
            "report_path": str(Path("tests/fixtures/report_mixed_b.json")),
            "dataset_name": "theme_pack",
            "slice_name": "2024_q4",
            "strategy_name": "mainline_trend_b",
            "symbol": "000001",
        },
        {
            "report_name": "mixed_c",
            "report_path": str(Path("tests/fixtures/report_mixed_c.json")),
            "dataset_name": "theme_pack",
            "slice_name": "2024_q4",
            "strategy_name": "mainline_trend_c",
            "symbol": "000001",
        },
        {
            "report_name": "stacked",
            "report_path": str(Path("tests/fixtures/report_stacked.json")),
            "dataset_name": "theme_pack",
            "slice_name": "2024_q2",
            "strategy_name": "mainline_trend_c",
            "symbol": "000002",
        },
    ]

    result = SpecialistFeatureGapAuditAnalyzer().analyze(report_specs=reports)

    assert result.summary["feature_gap_suspect_count"] == 2
    reasons = {row["reason"] for row in result.feature_gap_suspects}
    assert reasons == {"cross_strategy_mixed_repeat", "stacked_known_families"}
    assert result.summary["classification_counts"]["mixed_existing_families"] == 2
    assert result.summary["classification_counts"]["stacked_family_pocket"] == 1
