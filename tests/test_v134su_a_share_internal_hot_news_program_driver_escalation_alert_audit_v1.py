from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134su_a_share_internal_hot_news_program_driver_escalation_alert_audit_v1 import (
    V134SUAShareInternalHotNewsProgramDriverEscalationAlertAuditV1Analyzer,
)


def test_v134su_driver_escalation_alert_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SUAShareInternalHotNewsProgramDriverEscalationAlertAuditV1Analyzer(repo_root).analyze()

    assert report.summary["alert_row_count"] == 1
    assert report.summary["driver_escalation_priority"] in {"p0", "p1", "p2"}
    assert report.summary["program_driver_transition_class"] in {
        "no_previous_baseline",
        "stable",
        "activation_rotation",
        "hard_block_rotation",
        "noncritical_rotation",
    }
    assert report.summary["alert_state"] in {
        "high_priority_driver_escalation",
        "elevated_driver_escalation",
        "no_driver_escalation",
    }


def test_v134su_driver_escalation_alert_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SUAShareInternalHotNewsProgramDriverEscalationAlertAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["driver_escalation_alert"] == "read_ready_internal_only"
    assert rows["driver_transition"] == "materialized"
    assert rows["driver_escalation_priority"] == "materialized"
    assert rows["alert_state"] == "materialized"
