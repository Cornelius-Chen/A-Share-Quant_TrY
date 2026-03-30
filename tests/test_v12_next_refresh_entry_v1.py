from __future__ import annotations

from a_share_quant.strategy.v12_next_refresh_entry_v1 import V12NextRefreshEntryAnalyzer


def test_v12_next_refresh_entry_prepares_v4_refresh_entry() -> None:
    bottleneck_payload = {
        "summary": {
            "current_primary_bottleneck": "carry_row_diversity_gap",
            "first_lane_opening_led": True,
        }
    }
    next_refresh_design_payload = {
        "summary": {
            "recommended_next_batch_name": "market_research_v3_factor_diversity_seed",
        }
    }
    v3_audit_payload = {
        "summary": {
            "baseline_ready": True,
        }
    }
    first_lane_acceptance_payload = {
        "summary": {
            "lane_changes_carry_reading": False,
        }
    }

    result = V12NextRefreshEntryAnalyzer().analyze(
        bottleneck_payload=bottleneck_payload,
        next_refresh_design_payload=next_refresh_design_payload,
        v3_audit_payload=v3_audit_payload,
        first_lane_acceptance_payload=first_lane_acceptance_payload,
    )

    assert result.summary["acceptance_posture"] == "prepare_v12_next_refresh_entry_for_market_research_v4"
    assert result.summary["prepare_refresh_entry_now"] is True
    assert result.summary["prepare_manifest_now"] is False
    assert result.summary["recommended_next_batch_name"] == "market_research_v4_carry_row_diversity_refresh"
