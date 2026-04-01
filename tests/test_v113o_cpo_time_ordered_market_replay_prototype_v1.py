from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v113o_cpo_time_ordered_market_replay_prototype_v1 import (
    V113OCPOTimeOrderedMarketReplayPrototypeAnalyzer,
    load_json_report,
)


def test_v113o_cpo_time_ordered_market_replay_prototype() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V113OCPOTimeOrderedMarketReplayPrototypeAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports/analysis/v113n_cpo_real_board_episode_population_v1.json"),
    )

    assert result.summary["initial_capital"] == 1_000_000.0
    assert result.summary["margin_enabled"] is False
    assert result.summary["shorting_enabled"] is False
    assert result.summary["replay_trade_day_count"] > 0
    assert "open" in result.summary["supported_action_modes"]
