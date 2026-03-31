from __future__ import annotations

from a_share_quant.strategy.v12_v6_refresh_manifest_v1 import (
    V12V6RefreshManifestAnalyzer,
)


def test_v12_v6_refresh_manifest_opens_clean_catalyst_supported_training_gap_batch() -> None:
    reference_base_symbols = ["000099", "002273", "600760", "601989"]
    seed_universe_symbols = ["002085", "600118", "000738", "300474"]
    manifest_entries = [
        {
            "symbol": "002085",
            "target_training_gap": "true_carry_row",
            "primary_admission_reason": "true_carry_row",
            "row_hypothesis": "carry hypothesis",
            "catalyst_support_hypothesis": "policy followthrough",
            "catalyst_context_mode": "policy_followthrough",
        },
        {
            "symbol": "600118",
            "target_training_gap": "true_carry_row",
            "primary_admission_reason": "true_carry_row",
            "row_hypothesis": "carry hypothesis",
            "catalyst_support_hypothesis": "policy followthrough",
            "catalyst_context_mode": "policy_followthrough",
        },
        {
            "symbol": "000738",
            "target_training_gap": "clean_persistence_row",
            "primary_admission_reason": "clean_persistence_row",
            "row_hypothesis": "persistence hypothesis",
            "catalyst_support_hypothesis": "multi-day reinforcement",
            "catalyst_context_mode": "multi_day_reinforcement",
        },
        {
            "symbol": "300474",
            "target_training_gap": "clean_persistence_row",
            "primary_admission_reason": "clean_persistence_row",
            "row_hypothesis": "persistence hypothesis",
            "catalyst_support_hypothesis": "multi-day reinforcement",
            "catalyst_context_mode": "multi_day_reinforcement",
        },
    ]
    required_targets = ["true_carry_row", "clean_persistence_row"]

    result = V12V6RefreshManifestAnalyzer().analyze(
        reference_base_symbols=reference_base_symbols,
        seed_universe_symbols=seed_universe_symbols,
        manifest_entries=manifest_entries,
        required_targets=required_targets,
    )

    assert (
        result.summary["ready_to_bootstrap_market_research_v6_catalyst_supported_carry_persistence_refresh"]
        is True
    )
    assert result.summary["new_symbol_count"] == 4
    assert result.summary["target_counts"]["true_carry_row"] == 2
    assert result.summary["target_counts"]["clean_persistence_row"] == 2
    assert result.summary["missing_catalyst_support_count"] == 0
