from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ix_commercial_aerospace_iw_cross_theme_direction_triage_v1 import (
    V134IXCommercialAerospaceIWCrossThemeDirectionTriageV1Analyzer,
)


def test_v134ix_cross_theme_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IXCommercialAerospaceIWCrossThemeDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["theme_purity_label"] == "cross_theme_contaminated_watch"
    assert (
        result.summary["authoritative_status"]
        == "retain_000738_as_cross_theme_contaminated_watch_and_keep_true_selection_blocked"
    )
    triage_by_component = {row["component"]: row for row in result.triage_rows}
    assert (
        triage_by_component["000738"]["direction"]
        == "downshift_from_clean_second_carrier_watch_to_cross_theme_contaminated_watch"
    )
