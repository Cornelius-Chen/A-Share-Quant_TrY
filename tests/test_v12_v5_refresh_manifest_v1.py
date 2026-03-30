from __future__ import annotations

from a_share_quant.strategy.v12_v5_refresh_manifest_v1 import (
    V12V5RefreshManifestAnalyzer,
)


def test_v12_v5_refresh_manifest_opens_clean_training_gap_batch() -> None:
    reference_base_symbols = ["000725", "600150", "601919"]
    seed_universe_symbols = ["000099", "002273", "600760", "601989"]
    manifest_entries = [
        {
            "symbol": "000099",
            "target_training_gap": "true_carry_row",
            "primary_admission_reason": "true_carry_row",
            "row_hypothesis": "carry hypothesis",
        },
        {
            "symbol": "002273",
            "target_training_gap": "true_carry_row",
            "primary_admission_reason": "true_carry_row",
            "row_hypothesis": "carry hypothesis",
        },
        {
            "symbol": "600760",
            "target_training_gap": "clean_persistence_row",
            "primary_admission_reason": "clean_persistence_row",
            "row_hypothesis": "persistence hypothesis",
        },
        {
            "symbol": "601989",
            "target_training_gap": "clean_persistence_row",
            "primary_admission_reason": "clean_persistence_row",
            "row_hypothesis": "persistence hypothesis",
        },
    ]
    required_targets = ["true_carry_row", "clean_persistence_row"]

    result = V12V5RefreshManifestAnalyzer().analyze(
        reference_base_symbols=reference_base_symbols,
        seed_universe_symbols=seed_universe_symbols,
        manifest_entries=manifest_entries,
        required_targets=required_targets,
    )

    assert result.summary["ready_to_bootstrap_market_research_v5_carry_row_diversity_refresh"] is True
    assert result.summary["new_symbol_count"] == 4
    assert result.summary["target_counts"]["true_carry_row"] == 2
    assert result.summary["target_counts"]["clean_persistence_row"] == 2
