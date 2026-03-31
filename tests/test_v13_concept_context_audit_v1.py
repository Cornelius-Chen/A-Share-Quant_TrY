from __future__ import annotations

from a_share_quant.strategy.v13_concept_context_audit_v1 import V13ConceptContextAuditAnalyzer


def test_v13_concept_context_audit_stays_report_only() -> None:
    concept_source_fill_payload = {
        "fill_rows": [
            {
                "lane_outcome_label": "opening_led",
                "source_fill_status": "resolved_official_or_high_trust",
                "source_authority_tier": "official_industry",
                "persistence_class": "single_pulse",
                "mapped_context_name": "theme_a",
            },
            {
                "lane_outcome_label": "carry_row_present",
                "source_fill_status": "resolved_official_or_high_trust",
                "source_authority_tier": "official_industry",
                "persistence_class": "policy_followthrough",
                "mapped_context_name": "theme_b",
            },
        ]
    }

    result = V13ConceptContextAuditAnalyzer().analyze(
        concept_source_fill_payload=concept_source_fill_payload
    )

    assert result.summary["acceptance_posture"] == "open_v13_concept_context_audit_v1_as_bounded_report_only_check"
    assert result.summary["all_rows_resolved_source"] is True
    assert result.summary["promote_concept_branch_now"] is False
