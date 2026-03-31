from __future__ import annotations

from a_share_quant.strategy.v12_v6_refresh_criteria_v1 import (
    V12V6RefreshCriteriaAnalyzer,
)


def test_v12_v6_refresh_criteria_freezes_catalyst_supported_training_gap_rules() -> None:
    next_refresh_entry_payload = {
        "summary": {
            "prepare_refresh_entry_now": True,
            "recommended_next_batch_name": "market_research_v6_catalyst_supported_carry_persistence_refresh",
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
    catalyst_phase_check_payload = {
        "summary": {
            "keep_branch_report_only": True,
            "context_separation_present": True,
        }
    }

    result = V12V6RefreshCriteriaAnalyzer().analyze(
        next_refresh_entry_payload=next_refresh_entry_payload,
        training_manifest_payload=training_manifest_payload,
        carry_schema_payload=carry_schema_payload,
        catalyst_phase_check_payload=catalyst_phase_check_payload,
    )

    assert result.summary["acceptance_posture"] == "freeze_v12_v6_refresh_symbol_selection_criteria"
    assert result.summary["criteria_count"] == 9
    assert result.summary["additional_carry_rows_needed"] == 2
    assert result.summary["additional_persistence_rows_needed"] == 2
    assert result.summary["catalyst_branch_support_only"] is True
    assert result.summary["ready_to_open_v6_manifest_after_criteria"] is True
