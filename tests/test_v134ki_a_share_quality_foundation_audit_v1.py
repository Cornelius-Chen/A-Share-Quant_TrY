from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ki_a_share_quality_foundation_audit_v1 import (
    V134KIAShareQualityFoundationAuditV1Analyzer,
)


def test_v134ki_quality_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KIAShareQualityFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["materialized_source_quality_count"] == 36
    assert report.summary["materialized_event_quality_count"] == 52
    assert report.summary["high_authority_source_count"] > 0
    assert report.summary["bootstrap_evidence_gate_true_count"] > 0


def test_v134ki_quality_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KIAShareQualityFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["quality_component"]: row for row in report.quality_rows}

    assert rows["source_quality_registry"]["component_state"] == "materialized_bootstrap"
    assert rows["contradiction_backlog"]["component_state"] == "backlog_materialized_not_reviewed"
