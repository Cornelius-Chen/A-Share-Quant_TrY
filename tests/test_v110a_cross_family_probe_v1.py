from __future__ import annotations

from a_share_quant.strategy.v110a_cross_family_probe_v1 import V110ACrossFamilyProbeAnalyzer


def test_v110a_cross_family_probe_can_close_successfully_with_zero_admits() -> None:
    result = V110ACrossFamilyProbeAnalyzer().analyze(
        probe_protocol_payload={
            "summary": {"ready_for_single_probe_next": True},
            "protocol": {
                "existing_symbol_family_anchor": ["300750"],
                "sample_limit": 2,
            },
        },
        catalyst_seed_payload={
            "seed_rows": [
                {
                    "lane_outcome_label": "carry_row_present",
                    "persistence_class": "policy_followthrough",
                    "lane_id": "mainline_trend_b::2024-11-05::300750",
                    "symbol": "300750",
                    "event_date": "2024-11-05",
                },
                {
                    "lane_outcome_label": "carry_row_present",
                    "persistence_class": "policy_followthrough",
                    "lane_id": "mainline_trend_c::2024-11-05::300750",
                    "symbol": "300750",
                    "event_date": "2024-11-05",
                },
            ]
        },
        screened_collection_payload={
            "collection_rows": [
                {
                    "feature_name": "policy_followthrough_support",
                    "admission_status": "admit",
                    "lane_id": "mainline_trend_b::2024-11-05::300750",
                },
                {
                    "feature_name": "policy_followthrough_support",
                    "admission_status": "admit",
                    "lane_id": "mainline_trend_c::2024-11-05::300750",
                },
            ]
        },
    )

    assert result.summary["candidate_count"] == 2
    assert result.summary["admitted_case_count"] == 0
    assert result.summary["successful_negative_probe"] is True
