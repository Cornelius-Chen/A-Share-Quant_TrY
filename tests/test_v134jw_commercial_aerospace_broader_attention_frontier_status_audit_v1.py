from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jw_commercial_aerospace_broader_attention_frontier_status_audit_v1 import (
    V134JWCommercialAerospaceBroaderAttentionFrontierStatusAuditV1Analyzer,
)


def test_v134jw_frontier_status_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JWCommercialAerospaceBroaderAttentionFrontierStatusAuditV1Analyzer(repo_root).analyze()

    assert report.summary["frontier_state"] == "opened_protocol_only"
    assert report.summary["ready_local_broader_source_count"] == 3
    assert report.summary["same_plane_ready_source_count"] == 1
    assert report.summary["formalized_same_plane_branch_count"] == 3
    assert report.summary["promotive_branch_count"] == 0
    assert report.summary["blocked_consumer_count"] == 1


def test_v134jw_frontier_status_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JWCommercialAerospaceBroaderAttentionFrontierStatusAuditV1Analyzer(repo_root).analyze()
    rows = {row["branch"]: row for row in report.status_rows}

    assert rows["broader_symbol_pool_expander"]["operative_blocker"] == "name_to_symbol_coverage_gap"
    assert rows["heat_axis_and_counterpanel_expander"]["operative_blocker"] == "counterpanel_not_thickened"
    assert rows["carrier_follow_search_expander"]["operative_blocker"] == "branch_not_promotive"
    assert rows["capital_true_selection"]["operative_blocker"] == "all_three_live_branches_stop_before_promotion"
