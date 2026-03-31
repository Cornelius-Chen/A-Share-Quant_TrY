from __future__ import annotations

from a_share_quant.strategy.v13_concept_source_fill_v1 import V13ConceptSourceFillAnalyzer


def test_v13_concept_source_fill_uses_existing_source_layer() -> None:
    concept_seed_payload = {
        "seed_rows": [
            {"lane_id": "a"},
            {"lane_id": "b"},
        ]
    }
    source_fill_payload = {
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
                "source_fill_status": "resolved_official_or_high_trust",
                "persistence_class": "single_pulse",
            },
            {
                "lane_id": "b",
                "symbol": "300750",
                "lane_outcome_label": "carry_row_present",
                "mapped_context_name": "theme_b",
                "source_authority_tier": "official_industry",
                "policy_scope": "industry_norms",
                "execution_strength": "guidance",
                "rumor_risk_level": "low",
                "primary_source_ref": "ref_b",
                "source_fill_status": "resolved_official_or_high_trust",
                "persistence_class": "policy_followthrough",
            },
        ]
    }

    result = V13ConceptSourceFillAnalyzer().analyze(
        concept_seed_payload=concept_seed_payload,
        source_fill_payload=source_fill_payload,
    )

    assert result.summary["acceptance_posture"] == "open_v13_concept_source_fill_v1_as_bounded_theme_source_layer"
    assert result.summary["row_count"] == 2
    assert result.summary["resolved_source_count"] == 2
    assert result.summary["ready_for_concept_context_audit_next"] is True
