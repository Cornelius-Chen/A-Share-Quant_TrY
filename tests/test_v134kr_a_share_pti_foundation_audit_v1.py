from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kr_a_share_pti_foundation_audit_v1 import (
    V134KRASharePTIFoundationAuditV1Analyzer,
)


def test_v134kr_pti_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KRASharePTIFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["event_ledger_count"] == 52
    assert report.summary["time_slice_count"] > 0
    assert report.summary["state_transition_count"] == 57


def test_v134kr_pti_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KRASharePTIFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["pti_component"]: row for row in report.pti_rows}

    assert rows["event_ledger"]["component_state"] == "materialized_bootstrap"
    assert rows["transition_backlog"]["component_state"] == "backlog_materialized_not_bound_to_replay"
