from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kc_a_share_identity_foundation_audit_v1 import (
    V134KCAShareIdentityFoundationAuditV1Analyzer,
)


def test_v134kc_identity_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KCAShareIdentityFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["materialized_symbol_count"] == 82
    assert report.summary["input_source_file_count"] == 12
    assert report.summary["multi_source_symbol_count"] >= 40
    assert report.summary["materialized_alias_count"] >= 82


def test_v134kc_identity_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KCAShareIdentityFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["identity_component"]: row for row in report.identity_rows}

    assert rows["security_master"]["component_state"] == "materialized_foundation"
    assert rows["entity_alias_map"]["component_state"] == "materialized_foundation"
    assert rows["name_to_symbol_resolution"]["component_state"] == "seed_ready_from_alias_map"
