from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134za_a_share_internal_hot_news_sina_theme_probe_audit_v1 import (
    V134ZAAShareInternalHotNewsSinaThemeProbeAuditV1Analyzer,
)


def test_v134za_sina_theme_probe_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZAAShareInternalHotNewsSinaThemeProbeAuditV1Analyzer(repo_root).analyze()

    assert report.summary["fetch_row_count"] > 0
    assert report.summary["sample_row_count"] > 0


def test_v134za_sina_theme_probe_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZAAShareInternalHotNewsSinaThemeProbeAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: int(row["value"]) for row in report.rows}

    assert rows["fetch_row_count"] >= rows["theme_hit_count"]
