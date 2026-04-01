from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v115d_cpo_midfreq_action_outcome_training_table_v1 import (
    V115DCpoMidfreqActionOutcomeTrainingTableAnalyzer,
    load_json_report,
)


def test_v115d_cpo_midfreq_action_outcome_training_table() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V115DCpoMidfreqActionOutcomeTrainingTableAnalyzer(repo_root=repo_root)
    report, training_rows = analyzer.analyze(
        v114t_payload=load_json_report(repo_root / "reports/analysis/v114t_cpo_replay_integrity_repair_v1.json"),
        v115b_payload=load_json_report(repo_root / "reports/analysis/v115b_cpo_midfreq_intraday_factor_extraction_v1.json"),
        v115c_payload=load_json_report(repo_root / "reports/analysis/v115c_cpo_midfreq_intraday_miss_window_audit_v1.json"),
    )

    assert report.summary["training_row_count"] == len(training_rows)
    assert report.summary["training_row_count"] > 0
    assert report.summary["contains_add_vs_hold_rows"] is True
    assert report.summary["contains_reduce_close_rows"] is True
    assert any(bool(row["is_repaired_miss_window"]) for row in training_rows)
