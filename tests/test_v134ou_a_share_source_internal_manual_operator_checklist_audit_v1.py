from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ou_a_share_source_internal_manual_operator_checklist_audit_v1 import (
    V134OUAShareSourceInternalManualOperatorChecklistAuditV1Analyzer,
)


def test_source_internal_manual_operator_checklist_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OUAShareSourceInternalManualOperatorChecklistAuditV1Analyzer(repo_root).analyze()

    assert result.summary["checklist_row_count"] == 4
    assert result.summary["stage_1_count"] == 1
    assert result.summary["stage_2_count"] == 2
    assert result.summary["stage_3_count"] == 1


def test_source_internal_manual_operator_checklist_primary_stage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OUAShareSourceInternalManualOperatorChecklistAuditV1Analyzer(repo_root).analyze()

    primary = next(row for row in result.checklist_rows if row["checklist_stage"] == "stage_1_primary_host_family_review")
    assert primary["host"] == "finance.sina.com.cn"
    assert primary["operator_action_state"] == "manual_checklist_completed_pending_runtime_promotion"
