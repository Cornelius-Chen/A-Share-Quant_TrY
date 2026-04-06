from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135au_commercial_aerospace_training_admission_ledger_audit_v1 import (
    V135AUCommercialAerospaceTrainingAdmissionLedgerAuditV1Analyzer,
)


def test_v135au_training_admission_ledger_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AUCommercialAerospaceTrainingAdmissionLedgerAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 10
    assert result.summary["positive_support_sample_ready_count"] == 1
    assert result.summary["negative_support_sample_ready_count"] == 1
    assert result.summary["positive_sample_ready_count"] == 1
    assert result.summary["negative_sample_ready_count"] == 4
    assert result.summary["bridge_sample_ready_count"] == 1
    assert result.summary["subwindow_learning_only_count"] == 1
    assert result.summary["hold_count"] == 1
    assert result.summary["under_review_count"] == 0
