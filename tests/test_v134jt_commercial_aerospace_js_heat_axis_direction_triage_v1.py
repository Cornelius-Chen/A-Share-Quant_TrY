from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jt_commercial_aerospace_js_heat_axis_direction_triage_v1 import (
    V134JTCommercialAerospaceJSHeatAxisDirectionTriageV1Analyzer,
)


def test_v134jt_heat_axis_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JTCommercialAerospaceJSHeatAxisDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["same_plane_counterpanel_expansion_ready_count"] == 1
    assert report.summary["counterpanel_thickened_now"] is False
    assert (
        report.summary["authoritative_status"]
        == "treat_the_heat_axis_branch_as_formalized_but_not_yet_counterpanel_thickening_and_keep_true_selection_blocked"
    )


def test_v134jt_heat_axis_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JTCommercialAerospaceJSHeatAxisDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["realized_heat_axis_seed"] == "retain_as_same_plane_singleton_reinforcement_only"
    assert directions["forward_heat_axis_anchor"] == "retain_as_future_structure_not_current_counterpanel_thickener"
    assert directions["hard_counterpanel"] == "continue_treating_as_singleton"
    assert directions["capital_true_selection"] == "continue_blocked_while_counterpanel_remains_thin"
