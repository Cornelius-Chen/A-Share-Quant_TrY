from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jc_commercial_aerospace_symbol_named_heat_source_search_audit_v1 import (
    V134JCCommercialAerospaceSymbolNamedHeatSourceSearchAuditV1Analyzer,
)


def test_v134jc_symbol_named_heat_source_search_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134JCCommercialAerospaceSymbolNamedHeatSourceSearchAuditV1Analyzer(repo_root).analyze()

    assert result.summary["searched_source_count"] == 4
    assert result.summary["retained_symbol_named_heat_source_count"] == 1
    assert result.summary["second_symbol_named_heat_source_found"] is False
    assert result.summary["discarded_theme_heat_source_count"] == 2
    assert result.summary["forward_unresolved_heat_anchor_count"] == 1

    by_id = {row["registry_id"]: row for row in result.source_rows}
    assert by_id["ca_source_007"]["source_class"] == "retained_symbol_named_turning_point_heat_source"
    assert by_id["ca_source_004"]["source_class"] == "discarded_symbol_list_theme_heat_source"
    assert by_id["ca_anchor_004"]["source_class"] == "forward_unresolved_manual_heat_anchor"
