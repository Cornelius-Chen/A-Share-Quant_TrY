from __future__ import annotations

import csv
from pathlib import Path

from a_share_quant.strategy.v115h_cpo_high_dimensional_intraday_feature_base_table_v1 import (
    V115HCpoHighDimensionalIntradayFeatureBaseTableAnalyzer,
)


def test_v115h_high_dimensional_base_table_shape() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    with (repo_root / "data" / "training" / "cpo_midfreq_action_outcome_training_rows_enriched_v1.csv").open("r", encoding="utf-8") as handle:
        enriched_rows = list(csv.DictReader(handle))

    analyzer = V115HCpoHighDimensionalIntradayFeatureBaseTableAnalyzer(repo_root=repo_root)
    report, final_rows = analyzer.analyze(enriched_rows=enriched_rows)

    summary = report.summary
    assert summary["acceptance_posture"] == "freeze_v115h_cpo_high_dimensional_intraday_feature_base_table_v1"
    assert summary["actionable_row_count"] == 450
    assert summary["discoverable_feature_count"] > 25
    assert summary["continuous_feature_count"] > 22
    assert summary["binary_feature_count"] == 3
    assert summary["identity_fields_removed_from_distance_space"] is True
    assert len(final_rows) == 450

    first_row = final_rows[0]
    assert "f30_breakout_efficiency" in first_row
    assert "f30_breakout_efficiency_rz" in first_row
    assert "d5_30_close_vs_vwap" in first_row
    assert "d15_60_last_bar_volume_share_rz" in first_row
    assert "f30_upper_shadow_ratio" in first_row
    assert "f60_last_bar_upper_shadow_ratio_rz" in first_row
    assert "d15_60_last_bar_lower_shadow_ratio_rz" in first_row
    assert "symbol" in first_row
    assert "action_context" in first_row


def test_v115h_drops_identity_and_scale_noise_from_discovery_space() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    with (repo_root / "data" / "training" / "cpo_midfreq_action_outcome_training_rows_enriched_v1.csv").open("r", encoding="utf-8") as handle:
        enriched_rows = list(csv.DictReader(handle))

    analyzer = V115HCpoHighDimensionalIntradayFeatureBaseTableAnalyzer(repo_root=repo_root)
    report, _ = analyzer.analyze(enriched_rows=enriched_rows)

    audit_only = {row["field_name"] for row in report.audit_only_field_rows}
    dropped = {row["field_name"] for row in report.dropped_field_rows}

    assert "symbol" in audit_only
    assert "role_family" in audit_only
    assert "action_context" in audit_only
    assert "f30_amount_per_volume" in dropped
    assert "f60_intraday_return" in dropped
