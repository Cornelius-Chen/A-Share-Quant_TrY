from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class ExecutionIntent:
    trade_date: date
    symbol: str
    action: str
    quantity: int
    strategy_id: str
    source: str
    rationale: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AccountSnapshot:
    trade_date: date
    account_id: str
    cash: float
    equity: float
    gross_exposure: float
    net_exposure: float
    daily_turnover: float
    daily_loss_pct: float
    strategy_drawdown_pct: float
    account_drawdown_pct: float
    open_order_count: int
    open_position_count: int
    reduce_only_mode: bool = False
    strategy_halted: bool = False
    market_data_age_ms: int = 0
    position_snapshot_age_sec: int = 0
    risk_engine_available: bool = True
    broker_ack_healthy: bool = True


@dataclass(frozen=True, slots=True)
class PositionSnapshot:
    symbol: str
    quantity: int
    market_value: float
    strategy_weight: float
    account_weight: float
    add_count_today: int = 0
    order_count_today: int = 0
    sellable_quantity: int | None = None
    last_buy_trade_date: date | None = None


@dataclass(frozen=True, slots=True)
class SymbolMarketState:
    symbol: str
    trade_date: date
    board: str
    last_price: float
    turnover: float
    market_cap: float
    adv_5d: float
    adv_20d: float
    gap_up_pct: float
    gap_down_pct: float
    intraday_volatility: float
    is_limit_up: bool = False
    is_limit_down: bool = False
    is_near_limit_up: bool = False
    is_near_limit_down: bool = False
    is_suspended: bool = False
    is_st: bool = False
    listed_days: int = 0
    market_cap_reliable: bool = True


@dataclass(frozen=True, slots=True)
class PretradeDecision:
    approved: bool
    adjusted_quantity: int
    reasons: tuple[str, ...]
    observed: dict[str, Any]


@dataclass(frozen=True, slots=True)
class RiskDecision:
    allowed: bool
    size_multiplier: float
    posture: str
    reasons: tuple[str, ...]
    observed: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ExecutionOrder:
    trade_date: date
    symbol: str
    action: str
    quantity: int
    reference_price: float
    notional: float
    posture: str
    source: str
    rationale: str


@dataclass(frozen=True, slots=True)
class ExecutionAuditEvent:
    timestamp: datetime
    event_type: str
    symbol: str
    action: str
    accepted: bool
    reasons: tuple[str, ...]
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ExecutionPlan:
    orders: list[ExecutionOrder]
    blocked_intents: list[ExecutionIntent]
    audit_events: list[ExecutionAuditEvent]
    summary: dict[str, Any]
