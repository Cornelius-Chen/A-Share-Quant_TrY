from __future__ import annotations

from a_share_quant.strategy.v12_training_sample_manifest_v1 import (
    V12TrainingSampleManifestAnalyzer,
)


def test_v12_training_sample_manifest_keeps_opening_frozen_and_targets_carry() -> None:
    expansion_design_payload = {
        "summary": {
            "recommended_expansion_source": "future_refresh_rows_not_relabelled_existing_candidates"
        }
    }
    readiness_payload = {
        "summary": {
            "class_counts": {
                "opening_led": 6,
                "persistence_led": 2,
                "carry_row_present": 2,
            }
        }
    }

    result = V12TrainingSampleManifestAnalyzer().analyze(
        expansion_design_payload=expansion_design_payload,
        readiness_payload=readiness_payload,
    )

    assert result.summary["opening_count_frozen"] is True
    assert result.summary["additional_opening_rows_needed"] == 0
    assert result.summary["additional_persistence_rows_needed"] == 2
    assert result.summary["additional_carry_rows_needed"] == 2
    assert result.summary["allow_penalty_relabelling_into_carry"] is False
    assert result.summary["allow_deferred_basis_relabelling_into_carry"] is False
