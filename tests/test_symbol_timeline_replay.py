from __future__ import annotations

from a_share_quant.strategy.symbol_timeline_replay import SymbolTimelineReplay


def test_build_comparisons_reports_pnl_delta() -> None:
    replay = SymbolTimelineReplay()
    comparisons = replay._build_comparisons(
        candidate_records=[
            {
                "candidate_name": "shared_default",
                "strategy_name": "mainline_trend_a",
                "fills": [{}, {}],
                "closed_trades": [{"pnl": 100.0}, {"pnl": -20.0}],
            },
            {
                "candidate_name": "buffer_only_012",
                "strategy_name": "mainline_trend_a",
                "fills": [{}, {}],
                "closed_trades": [{"pnl": 90.0}, {"pnl": -50.0}],
            },
        ],
        incumbent_name="shared_default",
        challenger_name="buffer_only_012",
    )

    assert len(comparisons) == 1
    assert comparisons[0]["strategy_name"] == "mainline_trend_a"
    assert comparisons[0]["pnl_delta"] == -40.0
