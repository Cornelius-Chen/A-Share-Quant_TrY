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


def test_execution_engine_builds_minimal_plan() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    engine = ExecutionEngine(risk_limits_path=repo_root / "PROJECT_LIMITATION" / "risk_limits.yaml")
    plan = engine.build_plan(
        intents=[
            ExecutionIntent(
                trade_date=date(2026, 3, 31),
                symbol="300757",
                action="buy",
                quantity=2000,
                strategy_id="cpo_mainline",
                source="packaging_admission_extension",
                rationale="controlled packaging admission extension",
            ),
            ExecutionIntent(
                trade_date=date(2026, 3, 31),
                symbol="300308",
                action="sell",
                quantity=1000,
                strategy_id="cpo_mainline",
                source="core_leader_holding_veto",
                rationale="state-conditioned holding veto",
            ),
        ],
        account=AccountSnapshot(
            trade_date=date(2026, 3, 31),
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
            open_position_count=5,
        ),
        positions_by_symbol={
            "300308": PositionSnapshot(
                symbol="300308",
                quantity=1000,
                market_value=180_000.0,
                strategy_weight=0.15,
                account_weight=0.15,
            )
        },
        market_by_symbol={
            "300757": SymbolMarketState(
                symbol="300757",
                trade_date=date(2026, 3, 31),
                board="ChiNext",
                last_price=24.5,
                turnover=380_000_000.0,
                market_cap=8_500_000_000.0,
                adv_5d=900_000_000.0,
                adv_20d=700_000_000.0,
                gap_up_pct=0.018,
                gap_down_pct=0.0,
                intraday_volatility=0.041,
                listed_days=600,
            ),
            "300308": SymbolMarketState(
                symbol="300308",
                trade_date=date(2026, 3, 31),
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
            ),
        },
    )

    assert plan.summary["intent_count"] == 2
    assert plan.summary["planned_order_count"] == 2
    assert len(plan.audit_events) == 2
