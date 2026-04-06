from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ld_a_share_information_center_foundation_completion_audit_v1 import (
    V134LDAShareInformationCenterFoundationCompletionAuditV1Analyzer,
)


def test_v134ld_information_center_completion_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LDAShareInformationCenterFoundationCompletionAuditV1Analyzer(repo_root).analyze()

    assert report.summary["workstream_count"] == 13
    assert report.summary["foundation_complete_count"] == 13
    assert report.summary["open_execution_gate_count"] == 0


def test_v134ld_information_center_completion_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LDAShareInformationCenterFoundationCompletionAuditV1Analyzer(repo_root).analyze()

    assert any(row["workstream"] == "automation" for row in report.workstream_rows)
