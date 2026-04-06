from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135be_commercial_aerospace_training_task_ready_export_audit_v1 import (
    V135BECommercialAerospaceTrainingTaskReadyExportAuditV1Analyzer,
)


def test_v135be_training_task_ready_export_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135BECommercialAerospaceTrainingTaskReadyExportAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 30
    assert result.summary["unique_task_count"] == 6
    assert result.summary["fit_primary_row_count"] == 8
    assert result.summary["fit_auxiliary_row_count"] == 10
    assert result.summary["reference_only_row_count"] == 6
    assert result.summary["locked_holdout_row_count"] == 6
    assert result.summary["window_002_holdout_task_count"] == 6
