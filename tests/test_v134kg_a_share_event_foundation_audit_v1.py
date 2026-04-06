from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kg_a_share_event_foundation_audit_v1 import (
    V134KGAShareEventFoundationAuditV1Analyzer,
)


def test_v134kg_event_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KGAShareEventFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["input_registry_row_count"] == 52
    assert report.summary["materialized_document_count"] == 52
    assert report.summary["materialized_event_count"] == 52
    assert report.summary["materialized_source_count"] > 0


def test_v134kg_event_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KGAShareEventFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["event_component"]: row for row in report.event_rows}

    assert rows["source_master"]["component_state"] == "materialized_bootstrap"
    assert rows["event_registry"]["component_state"] == "materialized_bootstrap"
