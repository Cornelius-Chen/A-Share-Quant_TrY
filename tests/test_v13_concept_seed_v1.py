from __future__ import annotations

from a_share_quant.strategy.v13_concept_seed_v1 import V13ConceptSeedAnalyzer


def test_v13_concept_seed_uses_theme_scope_rows() -> None:
    concept_inventory_payload = {
        "summary": {
            "ready_for_bounded_concept_seed_next": True,
        }
    }
    catalyst_fill_payload = {
        "fill_rows": [
            {
                "lane_id": "a",
                "symbol": "002049",
                "strategy_name": "mainline_trend_c",
                "slice_name": "2024-11",
                "lane_outcome_label": "opening_led",
                "mapped_context_name": "theme_a",
                "mapping_source": "akshare_em_concept_history",
                "persistence_class": "single_pulse",
                "event_scope": "theme",
            },
            {
                "lane_id": "b",
                "symbol": "300750",
                "strategy_name": "mainline_trend_b",
                "slice_name": "2024-11",
                "lane_outcome_label": "carry_row_present",
                "mapped_context_name": "theme_b",
                "mapping_source": "akshare_em_concept_history",
                "persistence_class": "policy_followthrough",
                "event_scope": "theme",
            },
            {
                "lane_id": "c",
                "symbol": "300502",
                "strategy_name": "mainline_trend_c",
                "slice_name": "2024-06",
                "lane_outcome_label": "persistence_led",
                "mapped_context_name": "sector_x",
                "mapping_source": "akshare_cninfo",
                "persistence_class": "multi_day_reinforcement",
                "event_scope": "sector",
            },
        ]
    }

    result = V13ConceptSeedAnalyzer().analyze(
        concept_inventory_payload=concept_inventory_payload,
        catalyst_fill_payload=catalyst_fill_payload,
    )

    assert result.summary["acceptance_posture"] == "open_v13_concept_seed_v1_as_bounded_theme_scope_sample"
    assert result.summary["seed_row_count"] == 2
    assert result.summary["unique_symbol_count"] == 2
    assert result.summary["ready_for_concept_source_fill_next"] is True
