from __future__ import annotations

from a_share_quant.strategy.v12_v4_refresh_criteria_v1 import V12V4RefreshCriteriaAnalyzer


def test_v12_v4_refresh_criteria_freezes_selection_rules() -> None:
    next_refresh_entry_payload = {
        "summary": {
            "prepare_refresh_entry_now": True,
            "recommended_next_batch_name": "market_research_v4_carry_row_diversity_refresh",
        }
    }
    next_refresh_design_payload = {
        "target_rows": [
            {"target_name": "basis_spread_diversity"},
            {"target_name": "carry_duration_diversity"},
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
    carry_pilot_payload = {
        "summary": {
            "distinct_score_count": 1,
        }
    }

    result = V12V4RefreshCriteriaAnalyzer().analyze(
        next_refresh_entry_payload=next_refresh_entry_payload,
        next_refresh_design_payload=next_refresh_design_payload,
        carry_schema_payload=carry_schema_payload,
        carry_pilot_payload=carry_pilot_payload,
    )

    assert result.summary["acceptance_posture"] == "freeze_v12_v4_refresh_symbol_selection_criteria"
    assert result.summary["ready_to_open_v4_manifest_after_criteria"] is True
    assert result.summary["prepare_manifest_now"] is False
    assert result.summary["recommended_next_batch_name"] == "market_research_v4_carry_row_diversity_refresh"
