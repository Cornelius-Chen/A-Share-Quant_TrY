from __future__ import annotations

from a_share_quant.strategy.v112a_owner_correction_integration_v1 import (
    V112AOwnerCorrectionIntegrationAnalyzer,
)


def test_v112a_owner_correction_integration_applies_cycle_window_to_300308() -> None:
    result = V112AOwnerCorrectionIntegrationAnalyzer().analyze(
        label_review_sheet_payload={
            "review_rows": [
                {
                    "symbol": "300308",
                    "name": "中际旭创",
                    "pool_role_guess": "leader_or_core_beneficiary",
                    "include_in_first_pilot_guess": True,
                    "object_missing_or_extra_review": "owner_review_needed",
                    "cycle_window_correction_status": "owner_review_needed",
                    "owner_notes": "",
                }
            ]
        },
        owner_corrections={
            "symbol_corrections": {
                "300308": {
                    "include_in_first_pilot": True,
                    "cycle_window": {"major_markup_start": "2025-06"},
                    "owner_notes": "test",
                }
            }
        },
    )

    assert result.summary["resolved_cycle_count"] == 1
    assert result.integrated_rows[0]["final_role_label_cn"] == "龙头/核心受益股"
