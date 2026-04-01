from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from a_share_quant.execution.models import (
    AccountSnapshot,
    ExecutionAuditEvent,
    ExecutionIntent,
    ExecutionOrder,
    ExecutionPlan,
    PositionSnapshot,
    SymbolMarketState,
)
from a_share_quant.risk.pretrade_check import PretradeChecker
from a_share_quant.risk.risk_engine import RiskEngine


class ExecutionEngine:
    """Minimal research-to-execution planner: intent -> pretrade -> risk -> order/audit."""

    def __init__(self, *, risk_limits_path: Path) -> None:
        self.pretrade = PretradeChecker(risk_limits_path=risk_limits_path)
        self.risk = RiskEngine(risk_limits_path=risk_limits_path)

    def build_plan(
        self,
        *,
        intents: list[ExecutionIntent],
        account: AccountSnapshot,
        positions_by_symbol: dict[str, PositionSnapshot],
        market_by_symbol: dict[str, SymbolMarketState],
    ) -> ExecutionPlan:
        orders: list[ExecutionOrder] = []
        blocked: list[ExecutionIntent] = []
        audit_events: list[ExecutionAuditEvent] = []

        for intent in intents:
            market_state = market_by_symbol.get(intent.symbol)
            if market_state is None:
                blocked.append(intent)
                audit_events.append(
                    ExecutionAuditEvent(
                        timestamp=datetime.now(UTC),
                        event_type="market_state_missing",
                        symbol=intent.symbol,
                        action=intent.action,
                        accepted=False,
                        reasons=("missing_market_state",),
                        payload={"strategy_id": intent.strategy_id},
                    )
                )
                continue

            position = positions_by_symbol.get(intent.symbol)
            pretrade = self.pretrade.evaluate(
                intent=intent,
                account=account,
                position=position,
                market_state=market_state,
            )
            if not pretrade.approved:
                blocked.append(intent)
                audit_events.append(
                    ExecutionAuditEvent(
                        timestamp=datetime.now(UTC),
                        event_type="pretrade_block",
                        symbol=intent.symbol,
                        action=intent.action,
                        accepted=False,
                        reasons=pretrade.reasons,
                        payload=pretrade.observed,
                    )
                )
                continue

            risk = self.risk.evaluate(intent=intent, account=account)
            if not risk.allowed:
                blocked.append(intent)
                audit_events.append(
                    ExecutionAuditEvent(
                        timestamp=datetime.now(UTC),
                        event_type="risk_block",
                        symbol=intent.symbol,
                        action=intent.action,
                        accepted=False,
                        reasons=risk.reasons,
                        payload=risk.observed,
                    )
                )
                continue

            final_qty = int(pretrade.adjusted_quantity * risk.size_multiplier)
            if final_qty <= 0:
                blocked.append(intent)
                audit_events.append(
                    ExecutionAuditEvent(
                        timestamp=datetime.now(UTC),
                        event_type="zero_quantity_after_risk",
                        symbol=intent.symbol,
                        action=intent.action,
                        accepted=False,
                        reasons=("zero_quantity_after_risk",),
                        payload={"pretrade_qty": pretrade.adjusted_quantity, "risk_multiplier": risk.size_multiplier},
                    )
                )
                continue

            order = ExecutionOrder(
                trade_date=intent.trade_date,
                symbol=intent.symbol,
                action=intent.action,
                quantity=final_qty,
                reference_price=market_state.last_price,
                notional=round(final_qty * market_state.last_price, 4),
                posture=risk.posture,
                source=intent.source,
                rationale=intent.rationale,
            )
            orders.append(order)
            audit_events.append(
                ExecutionAuditEvent(
                    timestamp=datetime.now(UTC),
                    event_type="order_planned",
                    symbol=intent.symbol,
                    action=intent.action,
                    accepted=True,
                    reasons=tuple(list(pretrade.reasons) + list(risk.reasons)),
                    payload={
                        "quantity": final_qty,
                        "reference_price": market_state.last_price,
                        "notional": order.notional,
                        "risk_posture": risk.posture,
                    },
                )
            )

        summary = {
            "intent_count": len(intents),
            "planned_order_count": len(orders),
            "blocked_intent_count": len(blocked),
            "accepted_symbols": sorted({order.symbol for order in orders}),
            "blocked_symbols": sorted({intent.symbol for intent in blocked}),
        }
        return ExecutionPlan(
            orders=orders,
            blocked_intents=blocked,
            audit_events=audit_events,
            summary=summary,
        )
