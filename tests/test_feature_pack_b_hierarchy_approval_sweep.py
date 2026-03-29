from __future__ import annotations

from a_share_quant.strategy.feature_pack_b_hierarchy_approval_sweep import (
    FeaturePackBHierarchyApprovalSweepAnalyzer,
)


def test_candidate_row_counts_repairs_against_control() -> None:
    analyzer = FeaturePackBHierarchyApprovalSweepAnalyzer()
    control_daily = {
        "2024-01-01": {"permission_allowed": False, "assignment_layer": "junk", "emitted_actions": []},
        "2024-01-02": {"permission_allowed": True, "assignment_layer": "junk", "emitted_actions": []},
    }
    candidate_daily = {
        "2024-01-01": {"permission_allowed": True, "assignment_layer": "core", "emitted_actions": ["buy"]},
        "2024-01-02": {"permission_allowed": True, "assignment_layer": "leader", "emitted_actions": ["buy"]},
    }

    row = analyzer._candidate_row(
        candidate_name="candidate_a",
        daily=candidate_daily,
        control_daily=control_daily,
        trigger_dates=["2024-01-01", "2024-01-02"],
        total_pnl=123.4,
        trade_count=2,
        fill_count=3,
    )

    assert row["permission_repairs"] == 1
    assert row["assignment_repairs"] == 2
    assert row["emitted_buy_repairs"] == 2
    assert row["combined_repairs"] == 2
