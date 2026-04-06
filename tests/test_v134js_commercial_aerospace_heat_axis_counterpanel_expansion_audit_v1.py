from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134js_commercial_aerospace_heat_axis_counterpanel_expansion_audit_v1 import (
    V134JSCommercialAerospaceHeatAxisCounterpanelExpansionAuditV1Analyzer,
)


def test_v134js_heat_axis_counterpanel_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JSCommercialAerospaceHeatAxisCounterpanelExpansionAuditV1Analyzer(repo_root).analyze()

    assert report.summary["retained_heat_axis_source_count"] == 2
    assert report.summary["realized_heat_axis_source_count"] == 1
    assert report.summary["forward_heat_axis_anchor_count"] == 1
    assert report.summary["current_hard_counterpanel_count"] == 1
    assert report.summary["hard_anchor_grade_source_count"] == 1
    assert report.summary["counterpanel_thickened_now"] is False
    assert report.summary["same_plane_counterpanel_expansion_ready_count"] == 1


def test_v134js_heat_axis_rows_expected_roles() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JSCommercialAerospaceHeatAxisCounterpanelExpansionAuditV1Analyzer(repo_root).analyze()
    by_id = {row["registry_id"]: row for row in report.expansion_rows}

    assert by_id["ca_source_007"]["same_plane_usability"] == "same_plane_ready"
    assert by_id["ca_source_007"]["counterpanel_expansion_utility"] == "reinforces_existing_singleton"
    assert by_id["ca_anchor_004"]["same_plane_usability"] == "forward_only_not_same_plane"
    assert by_id["ca_anchor_004"]["counterpanel_expansion_utility"] == "future_structure_only"
