from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134si_a_share_internal_hot_news_program_snapshot_change_signal_audit_v1 import (
    V134SIAShareInternalHotNewsProgramSnapshotChangeSignalAuditV1Analyzer,
)


def test_v134si_program_snapshot_change_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SIAShareInternalHotNewsProgramSnapshotChangeSignalAuditV1Analyzer(repo_root).analyze()

    assert report.summary["change_row_count"] == 1
    assert report.summary["top_risk_change_state"] in {
        "no_previous_baseline",
        "stable",
        "minor_score_shift",
        "major_score_shift",
        "top_entity_changed",
    }
    assert report.summary["top_opportunity_change_state"] in {
        "no_previous_baseline",
        "stable",
        "minor_score_shift",
        "major_score_shift",
        "top_entity_changed",
    }
    assert report.summary["session_handling_mode_change"] in {
        "no_previous_baseline",
        "state_changed",
        "stable",
    }
    assert report.summary["signal_priority"] in {"p0", "p2"}


def test_v134si_program_snapshot_change_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134SIAShareInternalHotNewsProgramSnapshotChangeSignalAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["component_state"] for row in report.rows}

    assert rows["snapshot_change_signal"] == "read_ready_internal_only"
    assert rows["top_risk_change"] == "materialized"
    assert rows["session_change"] == "materialized"
    assert rows["signal_priority"] == "materialized"
