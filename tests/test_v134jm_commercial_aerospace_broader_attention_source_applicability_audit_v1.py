from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jm_commercial_aerospace_broader_attention_source_applicability_audit_v1 import (
    V134JMCommercialAerospaceBroaderAttentionSourceApplicabilityAuditV1Analyzer,
)


def test_v134jm_source_applicability_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JMCommercialAerospaceBroaderAttentionSourceApplicabilityAuditV1Analyzer(repo_root).analyze()

    assert report.summary["current_frontier_symbol_count"] == 8
    assert report.summary["market_snapshot_overlap_count"] == 3
    assert report.summary["theme_snapshot_overlap_count"] == 0
    assert report.summary["same_plane_ready_source_count"] == 1
    assert report.summary["structural_prior_only_source_count"] == 2
    assert report.summary["decisive_registry_temporal_alignment"] == "aligned_2026_event_surface"


def test_v134jm_source_rows_expected_applicability() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JMCommercialAerospaceBroaderAttentionSourceApplicabilityAuditV1Analyzer(repo_root).analyze()
    source_rows = {row["source_component"]: row for row in report.source_rows}

    assert source_rows["market_snapshot_inventory_v6"]["same_plane_applicability"] == "structural_prior_only_not_same_plane_live_evidence"
    assert source_rows["theme_snapshot_inventory_v7"]["same_plane_applicability"] == "theme_structure_prior_only_not_same_plane_live_evidence"
    assert source_rows["decisive_event_registry_v1"]["same_plane_applicability"] == "first_live_same_plane_expansion_source"
    assert source_rows["market_snapshot_inventory_v6"]["frontier_symbol_overlap"] == "000738|002085|600118"
    assert source_rows["theme_snapshot_inventory_v7"]["frontier_symbol_overlap"] == "none"
