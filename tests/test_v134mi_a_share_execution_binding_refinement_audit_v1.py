from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mi_a_share_execution_binding_refinement_audit_v1 import (
    V134MIAShareExecutionBindingRefinementAuditV1Analyzer,
)


def test_v134mi_execution_binding_refinement_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MIAShareExecutionBindingRefinementAuditV1Analyzer(repo_root).analyze()

    assert report.summary["blocker_count"] == 7
    assert report.summary["source_blocker_count"] == 2


def test_v134mi_execution_binding_refinement_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MIAShareExecutionBindingRefinementAuditV1Analyzer(repo_root).analyze()
    rows = {row["blocker_id"]: row for row in report.blocker_rows}

    assert rows["network_license_review_gate_closed"]["blocker_layer"] == "source_activation"
    assert rows["network_runtime_scheduler_gate_closed"]["blocker_layer"] == "source_activation"
