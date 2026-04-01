from __future__ import annotations

from datetime import date
from pathlib import Path

from a_share_quant.execution.engine import ExecutionEngine
from a_share_quant.execution.models import (
    AccountSnapshot,
    ExecutionIntent,
    PositionSnapshot,
    SymbolMarketState,
)


def test_sell_is_blocked_on_same_day_buy_under_t_plus_one() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    engine = ExecutionEngine(risk_limits_path=repo_root / "PROJECT_LIMITATION" / "risk_limits.yaml")
    today = date(2026, 3, 31)
    plan = engine.build_plan(
        intents=[
            ExecutionIntent(
                trade_date=today,
                symbol="300308",
                action="sell",
                quantity=1000,
                strategy_id="cpo_mainline",
                source="core_leader_holding_veto",
                rationale="same_day_sell_should_block",
            )
        ],
        account=AccountSnapshot(
            trade_date=today,
            account_id="demo_account",
            cash=800_000.0,
            equity=1_200_000.0,
            gross_exposure=0.55,
            net_exposure=0.55,
            daily_turnover=0.15,
            daily_loss_pct=0.004,
            strategy_drawdown_pct=0.03,
            account_drawdown_pct=0.04,
            open_order_count=2,
            open_position_count=1,
        ),
        positions_by_symbol={
            "300308": PositionSnapshot(
                symbol="300308",
                quantity=1000,
                market_value=180_000.0,
                strategy_weight=0.15,
                account_weight=0.15,
                sellable_quantity=0,
                last_buy_trade_date=today,
            )
        },
        market_by_symbol={
            "300308": SymbolMarketState(
                symbol="300308",
                trade_date=today,
                board="ChiNext",
                last_price=180.0,
                turnover=1_200_000_000.0,
                market_cap=55_000_000_000.0,
                adv_5d=2_100_000_000.0,
                adv_20d=1_800_000_000.0,
                gap_up_pct=0.0,
                gap_down_pct=0.012,
                intraday_volatility=0.056,
                listed_days=1200,
            )
        },
    )

    assert plan.summary["planned_order_count"] == 0
    assert plan.summary["blocked_intent_count"] == 1
    assert any("t_plus_one_sell_block" in event.reasons for event in plan.audit_events)
