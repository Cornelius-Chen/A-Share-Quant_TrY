from __future__ import annotations

from a_share_quant.strategy.v18c_screened_collection_v1 import V18CScreenedCollectionAnalyzer


def test_v18c_screened_collection_admits_bounded_cases_without_breaching_limits() -> None:
    result = V18CScreenedCollectionAnalyzer().analyze(
        screened_collection_protocol_payload={
            "summary": {"ready_for_screened_collection_next": True},
            "protocol": {
                "target_feature_rows": [
                    {
                        "feature_name": "single_pulse_support",
                        "sample_limit": 2,
                    },
                    {
                        "feature_name": "policy_followthrough_support",
                        "sample_limit": 1,
                    },
                ]
            },
        },
        catalyst_seed_payload={
            "seed_rows": [
                {
                    "lane_outcome_label": "opening_led",
                    "persistence_class": "single_pulse",
                    "lane_id": "a",
                    "symbol": "001",
                    "event_date": "2024-01-01",
                    "dataset_name": "seed",
                },
                {
                    "lane_outcome_label": "carry_row_present",
                    "persistence_class": "policy_followthrough",
                    "lane_id": "b",
                    "symbol": "002",
                    "event_date": "2024-01-02",
                    "dataset_name": "seed",
                },
            ]
        },
        market_v5_first_lane_payload={},
        market_v5_last_probe_payload={},
        market_v6_first_lane_payload={},
    )

    assert result.summary["acceptance_posture"] == "open_v18c_screened_collection_v1_as_bounded_collection"
    assert result.summary["targets_with_admitted_cases_count"] >= 1
    assert result.summary["sample_limit_breaches"] == 0
