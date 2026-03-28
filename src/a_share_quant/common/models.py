from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DailyBar:
    trade_date: date
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float
    pre_close: float
    adjust_factor: float
    is_st: bool = False
    is_suspended: bool = False
    listed_days: int = 0


@dataclass(frozen=True, slots=True)
class Signal:
    trade_date: date
    symbol: str
    action: str
    quantity: int


@dataclass(slots=True)
class Position:
    symbol: str
    quantity: int = 0
    average_cost: float = 0.0
    last_buy_date: date | None = None


@dataclass(frozen=True, slots=True)
class Fill:
    trade_date: date
    symbol: str
    action: str
    quantity: int
    price: float
    fees: float


@dataclass(frozen=True, slots=True)
class ClosedTrade:
    symbol: str
    entry_date: date
    exit_date: date
    quantity: int
    entry_price: float
    exit_price: float
    fees: float
    pnl: float
    holding_days: int


@dataclass(frozen=True, slots=True)
class EquityPoint:
    trade_date: date
    equity: float
    cash: float


@dataclass(slots=True)
class BacktestResult:
    fills: list[Fill]
    closed_trades: list[ClosedTrade]
    equity_curve: list[EquityPoint]
    rejected_signals: list[str]
    summary: dict[str, float | int | str]


@dataclass(slots=True)
class RunRecord:
    run_id: str
    run_type: str
    protocol_version: str
    strategy_family: str
    config_path: Path
    metadata_path: Path
    report_path: Path | None = None
    notes: str = ""
    extra: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SectorSnapshot:
    trade_date: date
    sector_id: str
    sector_name: str
    persistence: float
    diffusion: float
    money_making: float
    leader_strength: float
    relative_strength: float
    activity: float


@dataclass(frozen=True, slots=True)
class MainlineSectorScore:
    trade_date: date
    sector_id: str
    sector_name: str
    composite_score: float
    rank: int
    persistence: float
    diffusion: float
    money_making: float
    leader_strength: float
    relative_strength: float
    activity: float


@dataclass(frozen=True, slots=True)
class SampleSegment:
    segment_id: str
    method: str
    start_date: date
    end_date: date
    length: int
    trigger: str


@dataclass(frozen=True, slots=True)
class AttackPermission:
    trade_date: date
    is_attack_allowed: bool
    approved_sector_id: str | None
    approved_sector_name: str | None
    score: float | None
    reason: str


@dataclass(frozen=True, slots=True)
class StockSnapshot:
    trade_date: date
    symbol: str
    sector_id: str
    sector_name: str
    expected_upside: float
    drive_strength: float
    stability: float
    liquidity: float
    late_mover_quality: float
    resonance: float


@dataclass(frozen=True, slots=True)
class HierarchyAssignment:
    trade_date: date
    symbol: str
    sector_id: str
    sector_name: str
    layer: str
    layer_score: float
    leader_score: float
    core_score: float
    late_score: float
    reason: str


@dataclass(frozen=True, slots=True)
class TrendFilterDecision:
    trade_date: date
    symbol: str
    filter_name: str
    passed: bool
    reason: str


@dataclass(frozen=True, slots=True)
class EntryCandidate:
    trade_date: date
    symbol: str
    rule_name: str
    triggered: bool
    reason: str


@dataclass(frozen=True, slots=True)
class HoldingDecision:
    trade_date: date
    symbol: str
    should_hold: bool
    reason: str
    health_score: float


@dataclass(frozen=True, slots=True)
class ExitDecision:
    trade_date: date
    symbol: str
    should_exit: bool
    category: str
    reason: str


@dataclass(frozen=True, slots=True)
class MainlineWindow:
    window_id: str
    symbol: str
    start_date: date
    end_date: date
    capturable_return: float
