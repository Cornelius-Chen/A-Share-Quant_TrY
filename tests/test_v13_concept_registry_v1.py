from __future__ import annotations

from a_share_quant.strategy.v13_concept_registry_v1 import V13ConceptRegistryAnalyzer


def test_v13_concept_registry_stays_provisional_without_link_mode_proof() -> None:
    concept_seed_payload = {
        "seed_rows": [
            {
                "lane_id": "a",
                "strategy_name": "mainline_trend_c",
                "slice_name": "2024-11",
                "mapping_source": "akshare_em_concept_history",
            }
        ]
    }
    concept_source_fill_payload = {
        "fill_rows": [
            {
                "lane_id": "a",
                "symbol": "002049",
                "lane_outcome_label": "opening_led",
                "mapped_context_name": "theme_a",
                "source_authority_tier": "official_industry",
                "policy_scope": "industry_support",
                "execution_strength": "guidance",
                "rumor_risk_level": "low",
                "primary_source_ref": "ref_a",
                "persistence_class": "single_pulse",
                "source_fill_status": "resolved_official_or_high_trust",
            }
        ]
    }
    concept_mapping_confidence_payload = {
        "summary": {
            "acceptance_posture": "freeze_v13_concept_mapping_confidence_and_symbol_link_rules_v1"
        }
    }

    result = V13ConceptRegistryAnalyzer().analyze(
        concept_seed_payload=concept_seed_payload,
        concept_source_fill_payload=concept_source_fill_payload,
        concept_mapping_confidence_payload=concept_mapping_confidence_payload,
    )

    assert result.summary["acceptance_posture"] == "open_v13_concept_registry_v1_as_bounded_provisional_registry"
    assert result.summary["allowed_for_bounded_context_count"] == 1
    assert result.summary["provisional_market_confirmed_indirect_count"] == 1
    assert result.summary["core_confirmed_count"] == 0
