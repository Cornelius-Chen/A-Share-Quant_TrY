from __future__ import annotations

from a_share_quant.strategy.catalyst_context_audit_v1 import (
    CatalystContextAuditAnalyzer,
)


def test_catalyst_context_audit_detects_directional_separation_without_promotion() -> None:
    source_fill_payload = {
        "fill_rows": [
            {
                "lane_outcome_label": "opening_led",
                "persistence_class": "single_pulse",
                "event_scope": "sector",
                "source_fill_status": "unresolved",
            },
            {
                "lane_outcome_label": "opening_led",
                "persistence_class": "single_pulse",
                "event_scope": "theme",
                "source_fill_status": "resolved_official_or_high_trust",
            },
            {
                "lane_outcome_label": "persistence_led",
                "persistence_class": "multi_day_reinforcement",
                "event_scope": "theme",
                "source_fill_status": "resolved_official_or_high_trust",
            },
            {
                "lane_outcome_label": "carry_row_present",
                "persistence_class": "policy_followthrough",
                "event_scope": "theme",
                "source_fill_status": "resolved_official_or_high_trust",
            },
        ]
    }

    result = CatalystContextAuditAnalyzer().analyze(source_fill_payload=source_fill_payload)

    assert result.summary["opening_single_pulse_only"] is True
    assert result.summary["persistence_multi_day_only"] is True
    assert result.summary["carry_followthrough_only"] is True
    assert result.summary["context_separation_present"] is True
    assert result.summary["promote_catalyst_context_now"] is False
