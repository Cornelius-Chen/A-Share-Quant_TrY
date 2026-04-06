from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134rj_a_share_ri_internal_hot_news_signal_enrichment_direction_triage_v1 import (
    V134RJAShareRIInternalHotNewsSignalEnrichmentDirectionTriageV1Analyzer,
)


def test_v134rj_signal_enrichment_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RJAShareRIInternalHotNewsSignalEnrichmentDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["board_signal_row_count"] >= 0
    assert report.summary["important_queue_row_count"] >= 0


def test_v134rj_signal_enrichment_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RJAShareRIInternalHotNewsSignalEnrichmentDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "board_hit_state" in rows["mapping_enrichment"]
    assert "low-confidence" in rows["missing_surface_handling"]
