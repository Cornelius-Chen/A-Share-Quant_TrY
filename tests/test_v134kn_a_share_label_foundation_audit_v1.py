from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kn_a_share_label_foundation_audit_v1 import (
    V134KNAShareLabelFoundationAuditV1Analyzer,
)


def test_v134kn_label_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KNAShareLabelFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["label_definition_count"] == 15
    assert report.summary["label_assignment_count"] == 58
    assert report.summary["state_backlog_count"] == 4
    assert report.summary["governance_backlog_count"] == 2


def test_v134kn_label_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KNAShareLabelFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["label_component"]: row for row in report.label_rows}

    assert rows["label_registry"]["component_state"] == "materialized_bootstrap"
    assert rows["state_label_backlog"]["component_state"] == "backlog_materialized_not_assigned"
