from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134sy_a_share_internal_hot_news_program_control_packet_audit_v1 import (
    V134SYAShareInternalHotNewsProgramControlPacketAuditV1Analyzer,
)


def test_v134sy_program_control_packet_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SYAShareInternalHotNewsProgramControlPacketAuditV1Analyzer(repo_root).analyze()

    assert report.summary["packet_row_count"] == 1
    assert report.summary["program_driver_signal_mode"] in {"interrupt", "elevate_attention", "passive_polling"}
    assert report.summary["interrupt_required"] in {"true", "false"}
    assert report.summary["trading_day_state"] in {"trading_day_approx", "non_trading_day", "trading_day"}
    assert int(report.summary["primary_focus_source_present_count"]) >= 0
    assert report.summary["top_challenger_theme_slug"] not in {"", "none", report.summary["top_opportunity_primary_theme_slug"]}
    assert report.summary["challenger_review_attention_priority"] in {"p1", "p2", "p3"}
    assert report.summary["incumbent_is_focus_leader"] in {"true", "false"}
    assert report.summary["focus_governance_tension_priority"] in {"p1", "p2", "p3"}
    assert report.summary["focus_rotation_readiness_priority"] in {"p1", "p2", "p3"}
    if int(report.summary["primary_focus_source_present_count"]) == 0:
        assert report.summary["top_opportunity_theme_governance_state"] in {"accepted_rotation_override", "unknown"}


def test_v134sy_program_control_packet_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SYAShareInternalHotNewsProgramControlPacketAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["program_control_packet"] == "read_ready_internal_only"
    assert rows["driver_signal_mode"] == "materialized"
    assert rows["interrupt_required"] == "materialized"
    assert rows["top_risk_reference"] == "materialized"
    assert rows["top_opportunity_reference"] == "materialized"
    assert rows["primary_focus_replay_support"] == "materialized"
    assert rows["focus_competition_leaderboard"] == "materialized"
    assert rows["focus_governance_tension"] == "materialized"
    assert rows["focus_rotation_readiness"] == "materialized"
    assert rows["challenger_focus_board"] == "materialized"
    assert rows["challenger_review_attention"] == "materialized"
