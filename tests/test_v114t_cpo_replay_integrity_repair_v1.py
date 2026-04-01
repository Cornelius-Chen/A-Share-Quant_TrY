from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114t_cpo_replay_integrity_repair_v1 import (
    V114TCpoReplayIntegrityRepairAnalyzer,
    load_json_report,
)


def test_v114t_cpo_replay_integrity_repair() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114TCpoReplayIntegrityRepairAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v112aa_payload=load_json_report(repo_root / "reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json"),
        v113n_payload=load_json_report(repo_root / "reports/analysis/v113n_cpo_real_board_episode_population_v1.json"),
        v113t_payload=load_json_report(repo_root / "reports/analysis/v113t_cpo_execution_main_feed_build_v1.json"),
        v113u_payload=load_json_report(repo_root / "reports/analysis/v113u_cpo_execution_main_feed_readiness_audit_v1.json"),
    )

    assert result.summary["execution_timing"] == "signal_on_t_close_execute_on_t_plus_1_open"
    assert result.summary["t_plus_one_enabled"] is True
    assert result.summary["total_transaction_cost"] > 0
    assert result.executed_order_rows
    first_row = result.executed_order_rows[0]
    assert first_row["signal_trade_date"] < first_row["execution_trade_date"]
    assert first_row["total_cost"] > 0
