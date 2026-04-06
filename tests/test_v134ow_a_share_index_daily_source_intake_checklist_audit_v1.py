from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ow_a_share_index_daily_source_intake_checklist_audit_v1 import (
    V134OWAShareIndexDailySourceIntakeChecklistAuditV1Analyzer,
)


def test_index_daily_source_intake_checklist_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OWAShareIndexDailySourceIntakeChecklistAuditV1Analyzer(repo_root).analyze()

    assert result.summary["intake_step_count"] == 4
    assert result.summary["closed_step_count"] == 4


def test_index_daily_source_intake_checklist_states() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OWAShareIndexDailySourceIntakeChecklistAuditV1Analyzer(repo_root).analyze()

    assert all(row["current_state"] == "closed" for row in result.checklist_rows)
