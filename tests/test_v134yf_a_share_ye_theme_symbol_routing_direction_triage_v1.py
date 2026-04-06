from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134yf_a_share_ye_theme_symbol_routing_direction_triage_v1 import (
    V134YFAShareYEThemeSymbolRoutingDirectionTriageV1Analyzer,
)


def test_v134yf_theme_symbol_routing_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YFAShareYEThemeSymbolRoutingDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["case_count"] >= 10
    assert report.summary["direct_route_count"] >= 1


def test_v134yf_theme_symbol_routing_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YFAShareYEThemeSymbolRoutingDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
