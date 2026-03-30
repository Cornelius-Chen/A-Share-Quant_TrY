from __future__ import annotations

from a_share_quant.strategy.v12_next_refresh_factor_diversity_manifest_v1 import (
    V12NextRefreshFactorDiversityManifestAnalyzer,
)


def test_manifest_passes_when_all_targets_are_covered_with_new_symbols() -> None:
    result = V12NextRefreshFactorDiversityManifestAnalyzer().analyze(
        reference_base_symbols=["000001", "000333"],
        seed_universe_symbols=["002049", "300014", "600050", "603993"],
        manifest_entries=[
            {"symbol": "002049", "target_row_diversity": "basis_spread_diversity"},
            {"symbol": "300014", "target_row_diversity": "carry_duration_diversity"},
            {"symbol": "600050", "target_row_diversity": "exit_alignment_diversity"},
            {"symbol": "603993", "target_row_diversity": "cross_dataset_carry_reuse"},
        ],
        required_targets=[
            "basis_spread_diversity",
            "carry_duration_diversity",
            "exit_alignment_diversity",
            "cross_dataset_carry_reuse",
        ],
    )

    assert result.summary["ready_to_bootstrap_market_research_v3_factor_diversity_seed"] is True
    assert result.summary["missing_target_count"] == 0
    assert result.summary["overlap_with_reference_base_count"] == 0


def test_manifest_fails_when_a_required_target_is_missing() -> None:
    result = V12NextRefreshFactorDiversityManifestAnalyzer().analyze(
        reference_base_symbols=["000001", "000333"],
        seed_universe_symbols=["002049", "300014", "600050"],
        manifest_entries=[
            {"symbol": "002049", "target_row_diversity": "basis_spread_diversity"},
            {"symbol": "300014", "target_row_diversity": "carry_duration_diversity"},
            {"symbol": "600050", "target_row_diversity": "exit_alignment_diversity"},
        ],
        required_targets=[
            "basis_spread_diversity",
            "carry_duration_diversity",
            "exit_alignment_diversity",
            "cross_dataset_carry_reuse",
        ],
    )

    assert result.summary["ready_to_bootstrap_market_research_v3_factor_diversity_seed"] is False
    assert result.summary["missing_target_count"] == 1
