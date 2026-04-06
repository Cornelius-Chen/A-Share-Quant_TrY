from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jo_commercial_aerospace_decisive_event_registry_expansion_utility_audit_v1 import (
    V134JOCommercialAerospaceDecisiveEventRegistryExpansionUtilityAuditV1Analyzer,
)


def test_v134jo_decisive_registry_utility_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JOCommercialAerospaceDecisiveEventRegistryExpansionUtilityAuditV1Analyzer(repo_root).analyze()

    assert report.summary["same_plane_ready_source_count"] == 1
    assert report.summary["retained_registry_row_count"] == 12
    assert report.summary["broader_symbol_pool_expander_count"] == 4
    assert report.summary["heat_axis_and_counterpanel_expander_count"] == 2
    assert report.summary["carrier_follow_search_expander_count"] == 3
    assert report.summary["event_context_alignment_expander_count"] == 2
    assert report.summary["risk_constraint_anchor_expander_count"] == 1


def test_v134jo_utility_rows_contain_expected_class_examples() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JOCommercialAerospaceDecisiveEventRegistryExpansionUtilityAuditV1Analyzer(repo_root).analyze()
    by_id = {row["registry_id"]: row for row in report.utility_rows}

    assert by_id["ca_source_001"]["utility_class"] == "broader_symbol_pool_expander"
    assert by_id["ca_source_007"]["utility_class"] == "heat_axis_and_counterpanel_expander"
    assert by_id["ca_source_010"]["utility_class"] == "carrier_follow_search_expander"
    assert by_id["ca_anchor_002"]["utility_class"] == "event_context_alignment_expander"
    assert by_id["ca_anchor_001"]["utility_class"] == "risk_constraint_anchor_expander"
