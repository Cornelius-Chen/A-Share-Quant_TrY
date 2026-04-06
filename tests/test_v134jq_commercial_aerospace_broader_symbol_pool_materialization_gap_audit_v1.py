from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jq_commercial_aerospace_broader_symbol_pool_materialization_gap_audit_v1 import (
    V134JQCommercialAerospaceBroaderSymbolPoolMaterializationGapAuditV1Analyzer,
)


def test_v134jq_symbol_pool_gap_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JQCommercialAerospaceBroaderSymbolPoolMaterializationGapAuditV1Analyzer(repo_root).analyze()

    assert report.summary["broader_symbol_pool_expander_source_count"] == 4
    assert report.summary["broader_symbol_pool_extracted_candidate_total"] == 170
    assert report.summary["security_master_target_hit_count"] == 0
    assert report.summary["materialized_symbol_count"] == 0
    assert report.summary["authoritative_gap"] == "name_to_symbol_coverage_gap"


def test_v134jq_symbol_pool_gap_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JQCommercialAerospaceBroaderSymbolPoolMaterializationGapAuditV1Analyzer(repo_root).analyze()
    rows = {row["gap_component"]: row for row in report.gap_rows}

    assert rows["broader_symbol_pool_expander_sources"]["status"] == "candidate_names_present_but_not_normalized"
    assert rows["local_security_master_coverage"]["status"] == "zero_target_name_hits"
    assert rows["same_plane_symbol_pool_materialization"]["status"] == "blocked_by_name_to_symbol_coverage_gap"
