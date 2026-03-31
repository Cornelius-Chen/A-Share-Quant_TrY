from __future__ import annotations

from a_share_quant.strategy.v12_v6_phase_check_v1 import V12V6PhaseCheckAnalyzer


def test_v12_v6_phase_check_opens_first_lane_on_best_specialist_pocket() -> None:
    manifest_payload = {
        "summary": {
            "ready_to_bootstrap_market_research_v6_catalyst_supported_carry_persistence_refresh": True,
        }
    }
    training_manifest_payload = {
        "manifest_rows": [
            {"class_name": "opening_led", "additional_rows_needed": 0},
            {"class_name": "persistence_led", "additional_rows_needed": 2},
            {"class_name": "carry_row_present", "additional_rows_needed": 2},
        ]
    }
    specialist_analysis_payload = {
        "top_opportunities": [
            {
                "dataset_name": "market_research_v6_catalyst_supported_carry_persistence_refresh",
                "slice_name": "2024_q3",
                "strategy_name": "mainline_trend_c",
                "specialist_candidate": "baseline_expansion_branch",
            }
        ]
    }
    catalyst_phase_check_payload = {
        "summary": {
            "keep_branch_report_only": True,
        }
    }

    result = V12V6PhaseCheckAnalyzer().analyze(
        manifest_payload=manifest_payload,
        training_manifest_payload=training_manifest_payload,
        specialist_analysis_payload=specialist_analysis_payload,
        catalyst_phase_check_payload=catalyst_phase_check_payload,
    )

    assert result.summary["acceptance_posture"] == "open_first_v6_bounded_lane_on_best_specialist_pocket"
    assert result.summary["do_open_first_v6_lane_now"] is True
    assert result.summary["recommended_slice_name"] == "2024_q3"
    assert result.summary["recommended_strategy_name"] == "mainline_trend_c"
