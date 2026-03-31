from __future__ import annotations

from a_share_quant.strategy.v111a_screened_first_collection_v1 import (
    V111AScreenedFirstCollectionAnalyzer,
)


def test_v111a_screened_first_collection_admits_only_non_anchor_non_single_pulse_rows() -> None:
    result = V111AScreenedFirstCollectionAnalyzer().analyze(
        screened_collection_protocol_payload={
            "summary": {"ready_for_screened_collection_next": True},
            "protocol": {"candidate_cap": 5, "admission_cap": 2},
        },
        catalyst_source_fill_payload={
            "fill_rows": [
                {
                    "lane_id": "a",
                    "symbol": "300750",
                    "event_date": "2024-11-05",
                    "window_start": "2024-11-05",
                    "window_end": "2024-11-07",
                    "source_fill_status": "resolved_official_or_high_trust",
                    "board_pulse_breadth_class": "mapped_theme_present",
                    "persistence_class": "policy_followthrough",
                },
                {
                    "lane_id": "b",
                    "symbol": "000155",
                    "event_date": "2024-02-22",
                    "window_start": "2024-02-21",
                    "window_end": "2024-02-29",
                    "source_fill_status": "resolved_official_or_high_trust",
                    "board_pulse_breadth_class": "mapped_theme_present",
                    "persistence_class": "multi_day_reinforcement",
                },
                {
                    "lane_id": "c",
                    "symbol": "002049",
                    "event_date": "2024-11-05",
                    "window_start": "2024-11-05",
                    "window_end": "2024-11-08",
                    "source_fill_status": "resolved_official_or_high_trust",
                    "board_pulse_breadth_class": "mapped_theme_present",
                    "persistence_class": "single_pulse",
                },
            ]
        },
    )

    assert result.summary["admitted_candidate_count"] == 1
    assert result.summary["admitted_policy_followthrough_count"] == 0
    assert result.summary["sample_limit_breaches"] == 0
