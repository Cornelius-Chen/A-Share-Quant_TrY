from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from a_share_quant.execution.engine import ExecutionEngine
from a_share_quant.execution.models import (
    AccountSnapshot,
    ExecutionIntent,
    PositionSnapshot,
    SymbolMarketState,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    engine = ExecutionEngine(risk_limits_path=repo_root / "PROJECT_LIMITATION" / "risk_limits.yaml")

    intents = [
        ExecutionIntent(
            trade_date=date(2026, 3, 31),
            symbol="300757",
            action="buy",
            quantity=2000,
            strategy_id="cpo_mainline",
            source="packaging_admission_extension",
            rationale="controlled packaging admission extension",
            tags=("packaging", "admission"),
        ),
        ExecutionIntent(
            trade_date=date(2026, 3, 31),
            symbol="300308",
            action="sell",
            quantity=1000,
            strategy_id="cpo_mainline",
            source="core_leader_holding_veto",
            rationale="state-conditioned holding veto",
            tags=("core_leader", "holding_veto"),
        ),
    ]
    account = AccountSnapshot(
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
    )
    positions = {
        "300308": PositionSnapshot(
            symbol="300308",
            quantity=1000,
            market_value=180_000.0,
            strategy_weight=0.15,
            account_weight=0.15,
            add_count_today=0,
            order_count_today=1,
        )
    }
    market = {
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
    }

    plan = engine.build_plan(
        intents=intents,
        account=account,
        positions_by_symbol=positions,
        market_by_symbol=market,
    )

    payload = {
        "summary": plan.summary,
        "orders": [
            {
                "trade_date": str(order.trade_date),
                "symbol": order.symbol,
                "action": order.action,
                "quantity": order.quantity,
                "reference_price": order.reference_price,
                "notional": order.notional,
                "posture": order.posture,
                "source": order.source,
                "rationale": order.rationale,
            }
            for order in plan.orders
        ],
        "blocked_intents": [
            {
                "trade_date": str(intent.trade_date),
                "symbol": intent.symbol,
                "action": intent.action,
                "quantity": intent.quantity,
                "source": intent.source,
            }
            for intent in plan.blocked_intents
        ],
        "audit_events": [
            {
                "event_type": event.event_type,
                "symbol": event.symbol,
                "action": event.action,
                "accepted": event.accepted,
                "reasons": list(event.reasons),
                "payload": event.payload,
            }
            for event in plan.audit_events
        ],
    }
    output_path = repo_root / "reports" / "analysis" / "execution_demo_v1.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Execution demo written to: {output_path.relative_to(repo_root)}")
    print(f"Summary: {plan.summary}")


if __name__ == "__main__":
    main()
