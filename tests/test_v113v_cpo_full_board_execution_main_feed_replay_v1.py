from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113v_cpo_full_board_execution_main_feed_replay_v1 import (
    V113VCPOFullBoardExecutionMainFeedReplayAnalyzer,
    load_json_report,
)


def test_v113v_cpo_full_board_execution_main_feed_replay() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113VCPOFullBoardExecutionMainFeedReplayAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v112aa_payload=load_json_report(repo_root / "reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json"),
        v113n_payload=load_json_report(repo_root / "reports/analysis/v113n_cpo_real_board_episode_population_v1.json"),
        v113t_payload=load_json_report(repo_root / "reports/analysis/v113t_cpo_execution_main_feed_build_v1.json"),
        v113u_payload=load_json_report(repo_root / "reports/analysis/v113u_cpo_execution_main_feed_readiness_audit_v1.json"),
    )

    assert result.summary["initial_capital"] == 1_000_000.0
    assert result.summary["margin_enabled"] is False
    assert result.summary["shorting_enabled"] is False
    assert result.summary["t_plus_one_enabled"] is True
    assert result.summary["execution_main_feed_symbol_count"] == 20
    assert result.summary["replay_trade_day_count"] > 0
    assert "open" in result.summary["supported_action_modes"]
