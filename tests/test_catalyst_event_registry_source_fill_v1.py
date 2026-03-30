from __future__ import annotations

from a_share_quant.strategy.catalyst_event_registry_source_fill_v1 import (
    CatalystEventRegistrySourceFillAnalyzer,
)


def test_catalyst_event_registry_source_fill_allows_partial_resolution() -> None:
    market_context_fill_payload = {
        "fill_rows": [
            {"lane_id": "lane_a"},
            {"lane_id": "lane_b"},
        ]
    }
    source_entries = [
        {
            "lane_id": "lane_a",
            "source_fill_status": "resolved_official_or_high_trust",
            "source_authority_tier": "official_industry",
            "primary_source_ref": "https://example.com",
            "policy_scope": "industry_support",
            "execution_strength": "guidance",
            "rumor_risk_level": "low",
        }
    ]

    result = CatalystEventRegistrySourceFillAnalyzer().analyze(
        market_context_fill_payload=market_context_fill_payload,
        source_entries=source_entries,
    )

    assert result.summary["resolved_source_count"] == 1
    assert result.summary["unresolved_source_count"] == 1
    assert result.summary["ready_for_bounded_catalyst_context_audit"] is True
    assert result.fill_rows[0]["source_fill_status"] == "resolved_official_or_high_trust"
    assert result.fill_rows[1]["source_fill_status"] == "unresolved"
