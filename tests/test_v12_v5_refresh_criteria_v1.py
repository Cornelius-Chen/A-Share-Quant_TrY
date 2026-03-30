from __future__ import annotations

from a_share_quant.strategy.v12_v5_refresh_criteria_v1 import (
    V12V5RefreshCriteriaAnalyzer,
)


def test_v12_v5_refresh_criteria_freezes_training_gap_rules() -> None:
    next_refresh_entry_payload = {
        "summary": {
            "prepare_refresh_entry_now": True,
            "recommended_next_batch_name": "market_research_v5_carry_row_diversity_refresh",
        }
    }
    training_manifest_payload = {
        "manifest_rows": [
            {"class_name": "opening_led", "additional_rows_needed": 0},
            {"class_name": "persistence_led", "additional_rows_needed": 2},
            {"class_name": "carry_row_present", "additional_rows_needed": 2},
        ]
    }
    carry_schema_payload = {
        "summary": {
            "required_fields": [
                "basis_advantage_abs",
                "basis_advantage_bps",
                "challenger_carry_days",
                "same_exit_date",
                "pnl_delta_vs_closest",
            ]
        }
    }

    result = V12V5RefreshCriteriaAnalyzer().analyze(
        next_refresh_entry_payload=next_refresh_entry_payload,
        training_manifest_payload=training_manifest_payload,
        carry_schema_payload=carry_schema_payload,
    )

    assert result.summary["acceptance_posture"] == "freeze_v12_v5_refresh_symbol_selection_criteria"
    assert result.summary["criteria_count"] == 7
    assert result.summary["additional_carry_rows_needed"] == 2
    assert result.summary["additional_persistence_rows_needed"] == 2
    assert result.summary["ready_to_open_v5_manifest_after_criteria"] is True
