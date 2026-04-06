from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134yc_a_share_internal_hot_news_theme_symbol_hit_replay_audit_v1 import (
    V134YCAShareInternalHotNewsThemeSymbolHitReplayAuditV1Analyzer,
)


def test_v134yc_theme_symbol_hit_replay_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YCAShareInternalHotNewsThemeSymbolHitReplayAuditV1Analyzer(repo_root).analyze()

    assert report.summary["sample_row_count"] >= 1
    assert report.summary["theme_hit_count"] >= 0
    assert report.summary["theme_hit_with_symbol_watch_count"] >= 0


def test_v134yc_theme_symbol_hit_replay_rows_balance() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YCAShareInternalHotNewsThemeSymbolHitReplayAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: int(row["value"]) for row in report.rows}

    assert rows["sample_row_count"] == (
        rows["broad_market_only_count"]
        + rows["theme_hit_with_symbol_watch_count"]
        + rows["theme_hit_without_symbol_watch_count"]
    )
