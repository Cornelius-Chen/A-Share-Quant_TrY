from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134yd_a_share_yc_internal_hot_news_theme_symbol_hit_direction_triage_v1 import (
    V134YDAShareYCInternalHotNewsThemeSymbolHitDirectionTriageV1Analyzer,
)


def test_v134yd_theme_symbol_hit_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YDAShareYCInternalHotNewsThemeSymbolHitDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["sample_row_count"] >= 1
    assert report.summary["broad_market_only_count"] >= 0


def test_v134yd_theme_symbol_hit_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YDAShareYCInternalHotNewsThemeSymbolHitDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
