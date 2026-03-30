from __future__ import annotations

from a_share_quant.strategy.catalyst_event_registry_fill_v1 import (
    CatalystEventRegistryFillAnalyzer,
)


def test_catalyst_event_registry_fill_uses_local_market_context_first() -> None:
    seed_payload = {
        "seed_rows": [
            {
                "symbol": "002049",
                "event_date": "2024-11-05",
                "lane_outcome_label": "opening_led",
            },
            {
                "symbol": "300750",
                "event_date": "2024-11-05",
                "lane_outcome_label": "carry_row_present",
            },
        ]
    }
    concept_mapping_rows = [
        {
            "trade_date": "2024-11-05",
            "symbol": "002049",
            "concept_name": "通信技术",
            "mapping_source": "akshare_em_concept_history",
        }
    ]
    sector_mapping_rows = [
        {
            "trade_date": "2024-11-05",
            "symbol": "300750",
            "sector_name": "锂矿概念",
            "mapping_source": "akshare_em_concept_history",
        }
    ]

    result = CatalystEventRegistryFillAnalyzer().analyze(
        seed_payload=seed_payload,
        concept_mapping_rows=concept_mapping_rows,
        sector_mapping_rows=sector_mapping_rows,
    )

    assert result.summary["row_count"] == 2
    assert result.summary["market_context_filled_count"] == 2
    assert result.summary["official_source_filled_count"] == 0
    assert result.fill_rows[0]["event_scope"] == "theme"
    assert result.fill_rows[0]["event_type"] == "market_pulse"
    assert result.fill_rows[1]["event_type"] == "carry_context_candidate"
