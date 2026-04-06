from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v118f_cpo_add_vs_strong_entry_external_audit_v1 import (
    V118FCpoAddVsStrongEntryExternalAuditAnalyzer,
)


def test_v118f_add_vs_strong_entry_external_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V118FCpoAddVsStrongEntryExternalAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    assert result.summary["strong_entry_row_count"] == 5
    assert result.summary["best_balanced_accuracy"] >= 0.85

