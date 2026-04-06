from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zb_a_share_za_internal_hot_news_sina_probe_direction_triage_v1 import (
    V134ZBAShareZAInternalHotNewsSinaProbeDirectionTriageV1Analyzer,
)


def test_v134zb_sina_probe_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZBAShareZAInternalHotNewsSinaProbeDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["fetch_row_count"] > 0
    assert report.summary["theme_hit_count"] >= 0


def test_v134zb_sina_probe_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZBAShareZAInternalHotNewsSinaProbeDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
