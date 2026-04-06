from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qm_a_share_runtime_scheduler_activation_checklist_audit_v1 import (
    V134QMAShareRuntimeSchedulerActivationChecklistAuditV1Analyzer,
)


def test_v134qm_runtime_scheduler_checklist_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QMAShareRuntimeSchedulerActivationChecklistAuditV1Analyzer(repo_root).analyze()

    assert report.summary["checklist_step_count"] == 4
    assert report.summary["completed_step_count"] == 3
    assert report.summary["pending_step_count"] == 1
    assert report.summary["ready_to_open_now"] is False


def test_v134qm_runtime_scheduler_checklist_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QMAShareRuntimeSchedulerActivationChecklistAuditV1Analyzer(repo_root).analyze()
    rows = {row["checklist_step"]: row for row in report.checklist_rows}

    assert rows["step_3_activate_scheduler_runtime_binding"]["step_state"] == "pending"
    assert rows["step_1_confirm_single_runtime_candidate_lane"]["step_state"] == "completed"

