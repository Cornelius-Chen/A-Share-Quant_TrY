from __future__ import annotations

from a_share_quant.strategy.v12_v4_refresh_manifest_v1 import (
    V12V4RefreshManifestAnalyzer,
)


def test_v4_manifest_passes_when_targets_and_criteria_are_satisfied() -> None:
    result = V12V4RefreshManifestAnalyzer().analyze(
        reference_base_symbols=["000001", "002049"],
        seed_universe_symbols=["000725", "601127", "601919", "600570"],
        manifest_entries=[
            {
                "symbol": "000725",
                "target_row_diversity": "basis_spread_diversity",
                "carry_row_hypothesis": "Can add lower-basis semiconductor-adjacent carry rows.",
                "primary_admission_reason": "basis_spread_diversity",
            },
            {
                "symbol": "601127",
                "target_row_diversity": "carry_duration_diversity",
                "carry_row_hypothesis": "Can add longer carry duration rows in auto trend decay.",
                "primary_admission_reason": "carry_duration_diversity",
            },
            {
                "symbol": "601919",
                "target_row_diversity": "exit_alignment_diversity",
                "carry_row_hypothesis": "Can break same-exit alignment under slower shipping trend decay.",
                "primary_admission_reason": "exit_alignment_diversity",
            },
            {
                "symbol": "600570",
                "target_row_diversity": "cross_dataset_carry_reuse",
                "carry_row_hypothesis": "Can probe carry reuse in software outside current islands.",
                "primary_admission_reason": "cross_dataset_carry_reuse",
            },
        ],
        required_targets=[
            "basis_spread_diversity",
            "carry_duration_diversity",
            "exit_alignment_diversity",
            "cross_dataset_carry_reuse",
        ],
    )

    assert result.summary["ready_to_bootstrap_market_research_v4_carry_row_diversity_refresh"] is True
    assert result.summary["opening_clone_primary_count"] == 0


def test_v4_manifest_fails_when_primary_reason_is_opening_clone() -> None:
    result = V12V4RefreshManifestAnalyzer().analyze(
        reference_base_symbols=["000001"],
        seed_universe_symbols=["000725", "601127", "601919", "600570"],
        manifest_entries=[
            {
                "symbol": "000725",
                "target_row_diversity": "basis_spread_diversity",
                "carry_row_hypothesis": "Can add lower-basis semiconductor-adjacent carry rows.",
                "primary_admission_reason": "opening_led_clone",
            },
            {
                "symbol": "601127",
                "target_row_diversity": "carry_duration_diversity",
                "carry_row_hypothesis": "Can add longer carry duration rows in auto trend decay.",
                "primary_admission_reason": "carry_duration_diversity",
            },
            {
                "symbol": "601919",
                "target_row_diversity": "exit_alignment_diversity",
                "carry_row_hypothesis": "Can break same-exit alignment under slower shipping trend decay.",
                "primary_admission_reason": "exit_alignment_diversity",
            },
            {
                "symbol": "600570",
                "target_row_diversity": "cross_dataset_carry_reuse",
                "carry_row_hypothesis": "Can probe carry reuse in software outside current islands.",
                "primary_admission_reason": "cross_dataset_carry_reuse",
            },
        ],
        required_targets=[
            "basis_spread_diversity",
            "carry_duration_diversity",
            "exit_alignment_diversity",
            "cross_dataset_carry_reuse",
        ],
    )

    assert result.summary["ready_to_bootstrap_market_research_v4_carry_row_diversity_refresh"] is False
    assert result.summary["opening_clone_primary_count"] == 1
