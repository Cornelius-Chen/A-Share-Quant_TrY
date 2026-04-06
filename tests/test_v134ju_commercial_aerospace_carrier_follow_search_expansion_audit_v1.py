from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ju_commercial_aerospace_carrier_follow_search_expansion_audit_v1 import (
    V134JUCommercialAerospaceCarrierFollowSearchExpansionAuditV1Analyzer,
)


def test_v134ju_carrier_follow_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JUCommercialAerospaceCarrierFollowSearchExpansionAuditV1Analyzer(repo_root).analyze()

    assert report.summary["retained_supply_chain_source_count"] == 3
    assert report.summary["linked_local_case_count"] == 2
    assert report.summary["persistent_link_count"] == 1
    assert report.summary["moderate_link_count"] == 1
    assert report.summary["outside_named_watch_count"] == 1
    assert report.summary["branch_formalized"] is True
    assert report.summary["branch_promotive"] is False


def test_v134ju_carrier_follow_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JUCommercialAerospaceCarrierFollowSearchExpansionAuditV1Analyzer(repo_root).analyze()
    by_id = {row["registry_id"]: row for row in report.expansion_rows}

    assert by_id["ca_source_010"]["linked_symbol"] == "603601"
    assert by_id["ca_source_010"]["followthrough_label"] == "persistent_symbol_followthrough_without_board_unlock"
    assert by_id["ca_source_011"]["linked_symbol"] == "301306"
    assert by_id["ca_source_011"]["followthrough_label"] == "moderate_symbol_followthrough_without_board_unlock"
    assert by_id["ca_source_009"]["linked_symbol"] == "outside_named_candidate_watch"
    assert by_id["ca_source_009"]["expansion_reading"] == "same_plane_registry_support_exists_but_local_symbol_surface_not_materialized"
