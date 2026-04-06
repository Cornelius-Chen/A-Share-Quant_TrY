from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134iw_commercial_aerospace_000738_cross_theme_contamination_audit_v1 import (
    V134IWCommercialAerospace000738CrossThemeContaminationAuditV1Analyzer,
)


def test_v134iw_000738_cross_theme_contamination_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IWCommercialAerospace000738CrossThemeContaminationAuditV1Analyzer(repo_root).analyze()

    assert result.summary["primary_symbol"] == "000738"
    assert result.summary["theme_purity_label"] == "cross_theme_contaminated_watch"
    assert result.summary["comparator_absent_count"] == 2
    assert result.summary["broader_context_mode"] == "multi_day_reinforcement"

    by_symbol = {row["symbol"]: row for row in result.symbol_rows}
    assert by_symbol["000738"]["theme_purity_label"] == "cross_theme_contaminated_watch"
    assert (
        by_symbol["002353"]["theme_purity_label"]
        == "cross_theme_comparator_missing_from_current_local_surface"
    )
