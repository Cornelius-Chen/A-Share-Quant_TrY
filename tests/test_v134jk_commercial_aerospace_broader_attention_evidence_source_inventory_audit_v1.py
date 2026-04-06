from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jk_commercial_aerospace_broader_attention_evidence_source_inventory_audit_v1 import (
    V134JKCommercialAerospaceBroaderAttentionEvidenceSourceInventoryAuditV1Analyzer,
)


def test_v134jk_broader_attention_inventory_counts_and_readiness() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JKCommercialAerospaceBroaderAttentionEvidenceSourceInventoryAuditV1Analyzer(repo_root).analyze()

    assert report.summary["frontier_name"] == "broader_attention_evidence"
    assert report.summary["frontier_state"] == "opened_protocol_only"
    assert report.summary["ready_local_broader_source_count"] == 3
    assert report.summary["deferred_source_count"] == 1
    assert report.summary["blocked_consumer_count"] == 1
    assert report.summary["market_snapshot_row_count"] == 968
    assert report.summary["theme_snapshot_row_count"] == 3136
    assert report.summary["decisive_registry_row_count"] == 16
    assert report.summary["decisive_registry_retained_count"] == 12


def test_v134jk_contains_expected_source_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JKCommercialAerospaceBroaderAttentionEvidenceSourceInventoryAuditV1Analyzer(repo_root).analyze()
    source_rows = {row["source_component"]: row for row in report.source_rows}

    assert source_rows["board_local_event_attention_capital_handoff"]["readiness"] == "ready_as_frozen_input"
    assert source_rows["market_snapshot_inventory_v6"]["readiness"] == "ready_for_broader_attention_supervision"
    assert source_rows["theme_snapshot_inventory_v7"]["readiness"] == "ready_for_broader_attention_supervision"
    assert source_rows["decisive_event_registry_v1"]["readiness"] == "ready_for_broader_event_attention_supervision"
    assert source_rows["concept_purity_business_reference_layer"]["readiness"] == "deferred_until_future_full_a_share_coverage"
    assert source_rows["capital_true_selection_promotion"]["readiness"] == "still_blocked"
