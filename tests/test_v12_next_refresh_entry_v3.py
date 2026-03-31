from __future__ import annotations

from a_share_quant.strategy.v12_next_refresh_entry_v3 import (
    V12NextRefreshEntryV3Analyzer,
)


def test_v12_next_refresh_entry_v3_prepares_v6_refresh() -> None:
    v5_exhaustion_phase_check_payload = {
        "summary": {
            "do_prepare_next_refresh_entry_now": True,
        }
    }
    training_manifest_payload = {
        "manifest_rows": [
            {"class_name": "opening_led", "additional_rows_needed": 0},
            {"class_name": "persistence_led", "additional_rows_needed": 2},
            {"class_name": "carry_row_present", "additional_rows_needed": 2},
        ]
    }
    catalyst_phase_check_payload = {
        "summary": {
            "keep_branch_report_only": True,
        }
    }

    result = V12NextRefreshEntryV3Analyzer().analyze(
        v5_exhaustion_phase_check_payload=v5_exhaustion_phase_check_payload,
        training_manifest_payload=training_manifest_payload,
        catalyst_phase_check_payload=catalyst_phase_check_payload,
    )

    assert result.summary["acceptance_posture"] == "prepare_v12_next_refresh_entry_for_market_research_v6"
    assert (
        result.summary["recommended_next_batch_name"]
        == "market_research_v6_catalyst_supported_carry_persistence_refresh"
    )
    assert result.summary["additional_carry_rows_needed"] == 2
    assert result.summary["additional_persistence_rows_needed"] == 2
