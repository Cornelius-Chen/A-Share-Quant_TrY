from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ri_a_share_internal_hot_news_signal_enrichment_audit_v1 import (
    V134RIAShareInternalHotNewsSignalEnrichmentAuditV1Analyzer,
)


def test_v134ri_signal_enrichment_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RIAShareInternalHotNewsSignalEnrichmentAuditV1Analyzer(repo_root).analyze()

    assert report.summary["board_signal_row_count"] >= 0
    assert report.summary["important_queue_row_count"] >= 0
    assert report.summary["missing_surface_count"] >= 0


def test_v134ri_signal_enrichment_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RIAShareInternalHotNewsSignalEnrichmentAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["board_signal_enriched"] == "materialized"
    assert rows["important_queue_enriched"] == "materialized"
