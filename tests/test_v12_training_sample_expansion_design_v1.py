from __future__ import annotations

from a_share_quant.strategy.v12_training_sample_expansion_design_v1 import (
    V12TrainingSampleExpansionDesignAnalyzer,
)


def test_v12_training_sample_expansion_design_keeps_relabelling_closed() -> None:
    readiness_payload = {
        "summary": {
            "class_counts": {
                "opening_led": 6,
                "persistence_led": 2,
                "carry_row_present": 2,
            }
        }
    }
    factor_protocol_payload = {
        "factor_rows": [
            {"entry_name": "carry_in_basis_advantage", "evaluation_bucket": "evaluate_now"},
            {"entry_name": "preemptive_loss_avoidance_shift", "evaluation_bucket": "evaluate_with_penalty"},
            {"entry_name": "delayed_entry_basis_advantage", "evaluation_bucket": "hold_for_more_sample"},
        ]
    }
    registry_payload = {
        "registry_rows": [
            {"entry_name": "carry_in_basis_advantage", "bucket": "candidate_factor"}
        ]
    }

    result = V12TrainingSampleExpansionDesignAnalyzer().analyze(
        readiness_payload=readiness_payload,
        factor_protocol_payload=factor_protocol_payload,
        registry_payload=registry_payload,
    )

    assert result.summary["opening_sample_sufficient_now"] is True
    assert result.summary["persistence_sample_still_thin"] is True
    assert result.summary["carry_sample_still_thin"] is True
    assert result.summary["allow_relabelling_penalty_track_into_carry_class"] is False
    assert result.summary["allow_relabelling_deferred_basis_track_into_carry_class"] is False
