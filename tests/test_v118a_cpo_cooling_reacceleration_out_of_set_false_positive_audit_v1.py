from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v118a_cpo_cooling_reacceleration_out_of_set_false_positive_audit_v1 import (
    V118ACpoCoolingReaccelerationOutOfSetFalsePositiveAuditAnalyzer,
)


def test_v118a_out_of_set_false_positive_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V118ACpoCoolingReaccelerationOutOfSetFalsePositiveAuditAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
        threshold=489402000.0,
    )

    assert result.summary["authoritative_current_problem"] == "add_vs_entry_separation_not_reduce_or_close_contamination"
    assert result.summary["reduce_leakage_rate"] == 0.0
    assert result.summary["close_leakage_rate"] < result.summary["entry_leakage_rate"]
    assert len(result.leaked_entry_rows) == 4
