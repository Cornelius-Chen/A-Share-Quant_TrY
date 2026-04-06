from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sb_a_share_sa_internal_hot_news_rolling_context_direction_triage_v1 import (
    V134SBAShareSAInternalHotNewsRollingContextDirectionTriageV1Analyzer,
)


def test_v134sb_rolling_context_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SBAShareSAInternalHotNewsRollingContextDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["context_row_count"] > 0


def test_v134sb_rolling_context_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SBAShareSAInternalHotNewsRollingContextDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "rolling_context_surface" in rows["rolling_context_delivery"]
    assert "recency-weighted_signal" in rows["rolling_context_delivery"]
    assert "impact_window_surface" in rows["important_memory_delivery"]
