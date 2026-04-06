from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135as_a_share_internal_hot_news_focus_governance_tension_change_signal_audit_v1 import (
    V135ASAShareInternalHotNewsFocusGovernanceTensionChangeSignalAuditV1Analyzer,
)


def test_v135as_focus_governance_tension_change_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ASAShareInternalHotNewsFocusGovernanceTensionChangeSignalAuditV1Analyzer(
        repo_root
    ).analyze()

    assert report.summary["signal_row_count"] == 1
    assert report.summary["signal_priority"] in {"p1", "p2"}
    assert report.summary["tension_state_change"] in {"no_previous_baseline", "state_changed", "stable"}


def test_v135as_focus_governance_tension_change_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135ASAShareInternalHotNewsFocusGovernanceTensionChangeSignalAuditV1Analyzer(
        repo_root
    ).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert rows["current_primary_rank_change"] in {"no_previous_baseline", "state_changed", "stable"}
