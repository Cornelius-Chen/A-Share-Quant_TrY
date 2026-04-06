from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ye_a_share_theme_symbol_routing_drill_audit_v1 import (
    V134YEAShareThemeSymbolRoutingDrillAuditV1Analyzer,
)


def test_v134ye_theme_symbol_routing_drill_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YEAShareThemeSymbolRoutingDrillAuditV1Analyzer(repo_root).analyze()

    assert report.summary["case_count"] >= 10
    assert report.summary["routed_count"] >= 1


def test_v134ye_theme_symbol_routing_drill_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134YEAShareThemeSymbolRoutingDrillAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: int(row["value"]) for row in report.rows}

    assert rows["case_count"] >= rows["routed_count"]
