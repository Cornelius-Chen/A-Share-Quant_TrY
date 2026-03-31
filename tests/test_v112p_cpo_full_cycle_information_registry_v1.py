from __future__ import annotations

from a_share_quant.strategy.v112p_cpo_full_cycle_information_registry_v1 import (
    V112PCPOFullCycleInformationRegistryAnalyzer,
)


def test_v112p_registry_freezes_broad_layers_and_cohort() -> None:
    result = V112PCPOFullCycleInformationRegistryAnalyzer().analyze(
        phase_charter_payload={"summary": {"do_open_v112p_now": True}},
        study_scope_payload={
            "candidate_rows": [
                {"symbol_or_name": "002281", "study_tier": "review_only_adjacent_candidate"},
                {"symbol_or_name": "603083", "study_tier": "review_only_adjacent_candidate"},
                {"symbol_or_name": "688205", "study_tier": "review_only_adjacent_candidate"},
                {"symbol_or_name": "301205", "study_tier": "review_only_adjacent_candidate"},
                {"symbol_or_name": "300620", "study_tier": "review_only_adjacent_candidate"},
                {"symbol_or_name": "300548", "study_tier": "review_only_adjacent_candidate"},
            ]
        },
        pilot_dataset_payload={
            "dataset_rows": [
                {"symbol": "300308"},
                {"symbol": "300502"},
                {"symbol": "300394"},
            ]
        },
    )

    assert result.summary["information_layer_count"] >= 5
    assert result.summary["cohort_row_count"] >= 15
    assert result.summary["validated_core_count"] == 3
