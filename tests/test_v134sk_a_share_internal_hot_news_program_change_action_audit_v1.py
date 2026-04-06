from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sk_a_share_internal_hot_news_program_change_action_audit_v1 import (
    V134SKAShareInternalHotNewsProgramChangeActionAuditV1Analyzer,
)


def test_v134sk_program_change_action_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SKAShareInternalHotNewsProgramChangeActionAuditV1Analyzer(repo_root).analyze()

    assert report.summary["action_row_count"] == 1
    assert report.summary["global_program_action_mode"] in {
        "risk_first_mode",
        "opportunity_first_mode",
        "dual_focus_risk_and_opportunity",
        "balanced_observe_mode",
    }
    assert report.summary["session_action_gate"] in {
        "allow_live_routing",
        "hold_context_no_new_session_push",
        "prepare_only_before_continuous_session",
        "review_only_after_close",
        "watch_only_non_trading_day",
    }


def test_v134sk_program_change_action_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SKAShareInternalHotNewsProgramChangeActionAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["change_action_surface"] == "read_ready_internal_only"
    assert rows["global_program_action_mode"] == "materialized"
    assert rows["session_action_gate"] == "materialized"
