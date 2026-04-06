from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v118c_cpo_add_vs_entry_external_audit_v1 import (
    V118CCpoAddVsEntryExternalAuditAnalyzer,
)


def test_v118c_add_vs_entry_external_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V118CCpoAddVsEntryExternalAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    assert result.summary["candidate_name"] == "add_vs_strong_entry_separation_score_candidate"
    assert result.summary["best_balanced_accuracy"] >= 0.75
    assert result.summary["mean_gap_positive_add_minus_entry"] > 0

