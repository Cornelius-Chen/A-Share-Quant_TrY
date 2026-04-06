from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ta_a_share_internal_hot_news_program_control_packet_change_signal_audit_v1 import (
    V134TAAShareInternalHotNewsProgramControlPacketChangeSignalAuditV1Analyzer,
)


def test_v134ta_program_control_packet_change_signal_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TAAShareInternalHotNewsProgramControlPacketChangeSignalAuditV1Analyzer(repo_root).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["signal_priority"] in {"p1", "p2"}
    assert report.summary["program_driver_signal_mode_change"] in {"no_previous_baseline", "state_changed", "stable"}
    assert report.summary["interrupt_required_change"] in {"no_previous_baseline", "state_changed", "stable"}


def test_v134ta_program_control_packet_change_signal_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134TAAShareInternalHotNewsProgramControlPacketChangeSignalAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["control_packet_change_signal"] == "read_ready_internal_only"
    assert rows["driver_signal_mode_change"] == "materialized"
    assert rows["interrupt_required_change"] == "materialized"
    assert rows["top_risk_reference_change"] == "materialized"
    assert rows["top_opportunity_reference_change"] == "materialized"
    assert rows["top_watch_symbol_change"] == "materialized"
    assert rows["primary_focus_replay_support_change"] == "materialized"
    assert rows["challenger_focus_change"] == "materialized"
    assert rows["challenger_review_attention_change"] == "materialized"
    assert rows["focus_governance_tension_change"] == "materialized"
    assert rows["focus_rotation_readiness_change"] == "materialized"
