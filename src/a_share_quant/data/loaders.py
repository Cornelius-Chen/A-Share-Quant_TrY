from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from a_share_quant.common.models import (
    ConceptMappingRecord,
    DailyBar,
    MainlineWindow,
    SecurityMasterRecord,
    SectorMappingRecord,
    SectorSnapshot,
    Signal,
    StockSnapshot,
    TradingCalendarEntry,
)


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def load_daily_bars_from_csv(path: Path) -> list[DailyBar]:
    """Load daily A-share bars from a CSV file."""
    bars: list[DailyBar] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            bars.append(
                DailyBar(
                    trade_date=date.fromisoformat(row["trade_date"]),
                    symbol=row["symbol"],
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                    turnover=float(row["turnover"]),
                    pre_close=float(row["pre_close"]),
                    adjust_factor=float(row.get("adjust_factor", 1.0) or 1.0),
                    is_st=_parse_bool(row.get("is_st", "false")),
                    is_suspended=_parse_bool(row.get("is_suspended", "false")),
                    listed_days=int(row.get("listed_days", 0) or 0),
                )
            )
    return bars


def load_signals_from_csv(path: Path) -> list[Signal]:
    """Load pre-generated buy or sell signals from a CSV file."""
    signals: list[Signal] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            signals.append(
                Signal(
                    trade_date=date.fromisoformat(row["trade_date"]),
                    symbol=row["symbol"],
                    action=row["action"].strip().lower(),
                    quantity=int(row["quantity"]),
                )
            )
    return signals


def load_sector_snapshots_from_csv(path: Path) -> list[SectorSnapshot]:
    """Load sector-level snapshots used for mainline scoring."""
    snapshots: list[SectorSnapshot] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            snapshots.append(
                SectorSnapshot(
                    trade_date=date.fromisoformat(row["trade_date"]),
                    sector_id=row["sector_id"],
                    sector_name=row["sector_name"],
                    persistence=float(row["persistence"]),
                    diffusion=float(row["diffusion"]),
                    money_making=float(row["money_making"]),
                    leader_strength=float(row["leader_strength"]),
                    relative_strength=float(row["relative_strength"]),
                    activity=float(row["activity"]),
                )
            )
    return snapshots


def load_stock_snapshots_from_csv(path: Path) -> list[StockSnapshot]:
    """Load stock-level snapshots used for hierarchy ranking."""
    snapshots: list[StockSnapshot] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            snapshots.append(
                StockSnapshot(
                    trade_date=date.fromisoformat(row["trade_date"]),
                    symbol=row["symbol"],
                    sector_id=row["sector_id"],
                    sector_name=row["sector_name"],
                    expected_upside=float(row["expected_upside"]),
                    drive_strength=float(row["drive_strength"]),
                    stability=float(row["stability"]),
                    liquidity=float(row["liquidity"]),
                    late_mover_quality=float(row["late_mover_quality"]),
                    resonance=float(row["resonance"]),
                    concept_support=float(row.get("concept_support", 0.0) or 0.0),
                    primary_concept_weight=float(row.get("primary_concept_weight", 0.0) or 0.0),
                    concept_count=int(row.get("concept_count", 0) or 0),
                    concept_concentration_ratio=float(
                        row.get("concept_concentration_ratio", 0.0) or 0.0
                    ),
                    leader_component_score=float(
                        row.get("leader_component_score", 0.0) or 0.0
                    ),
                    core_component_score=float(
                        row.get("core_component_score", 0.0) or 0.0
                    ),
                    late_component_score=float(
                        row.get("late_component_score", 0.0) or 0.0
                    ),
                    non_junk_composite_score=float(
                        row.get("non_junk_composite_score", 0.0) or 0.0
                    ),
                    late_quality_raw_score=float(
                        row.get("late_quality_raw_score", 0.0) or 0.0
                    ),
                    late_quality_concept_boost=float(
                        row.get("late_quality_concept_boost", 0.0) or 0.0
                    ),
                    late_quality_sector_strength=float(
                        row.get("late_quality_sector_strength", 0.0) or 0.0
                    ),
                    late_quality_lag_balance=float(
                        row.get("late_quality_lag_balance", 0.0) or 0.0
                    ),
                    late_quality_trend_support=float(
                        row.get("late_quality_trend_support", 0.0) or 0.0
                    ),
                    stability_volatility=float(
                        row.get("stability_volatility", 0.0) or 0.0
                    ),
                    liquidity_turnover_share=float(
                        row.get("liquidity_turnover_share", 0.0) or 0.0
                    ),
                    liquidity_turnover_rank=float(
                        row.get("liquidity_turnover_rank", 0.0) or 0.0
                    ),
                    liquidity_sector_turnover_share=float(
                        row.get("liquidity_sector_turnover_share", 0.0) or 0.0
                    ),
                    liquidity_sector_top_turnover_share=float(
                        row.get("liquidity_sector_top_turnover_share", 0.0) or 0.0
                    ),
                    liquidity_sector_mean_turnover_share=float(
                        row.get("liquidity_sector_mean_turnover_share", 0.0) or 0.0
                    ),
                    liquidity_sector_turnover_share_gap=float(
                        row.get("liquidity_sector_turnover_share_gap", 0.0) or 0.0
                    ),
                    liquidity_sector_symbol_count=int(
                        row.get("liquidity_sector_symbol_count", 0) or 0
                    ),
                    context_theme_density=float(
                        row.get("context_theme_density", 0.0) or 0.0
                    ),
                    context_turnover_concentration=float(
                        row.get("context_turnover_concentration", 0.0) or 0.0
                    ),
                    context_theme_turnover_interaction=float(
                        row.get("context_theme_turnover_interaction", 0.0) or 0.0
                    ),
                    context_sector_heat=float(
                        row.get("context_sector_heat", 0.0) or 0.0
                    ),
                    context_sector_breadth=float(
                        row.get("context_sector_breadth", 0.0) or 0.0
                    ),
                    late_quality_sector_contribution=float(
                        row.get("late_quality_sector_contribution", 0.0) or 0.0
                    ),
                    late_quality_stability_contribution=float(
                        row.get("late_quality_stability_contribution", 0.0) or 0.0
                    ),
                    late_quality_liquidity_contribution=float(
                        row.get("late_quality_liquidity_contribution", 0.0) or 0.0
                    ),
                    late_quality_lag_contribution=float(
                        row.get("late_quality_lag_contribution", 0.0) or 0.0
                    ),
                    late_quality_trend_contribution=float(
                        row.get("late_quality_trend_contribution", 0.0) or 0.0
                    ),
                )
            )
    return snapshots


def load_mainline_windows_from_csv(path: Path) -> list[MainlineWindow]:
    """Load protocol-level mainline windows used by custom metrics."""
    windows: list[MainlineWindow] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            windows.append(
                MainlineWindow(
                    window_id=row["window_id"],
                    symbol=row["symbol"],
                    start_date=date.fromisoformat(row["start_date"]),
                    end_date=date.fromisoformat(row["end_date"]),
                    capturable_return=float(row["capturable_return"]),
                )
            )
    return windows


def load_trading_calendar_from_csv(path: Path) -> list[TradingCalendarEntry]:
    """Load trading-calendar entries from a canonical CSV file."""
    entries: list[TradingCalendarEntry] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            entries.append(
                TradingCalendarEntry(
                    trade_date=date.fromisoformat(row["trade_date"]),
                    is_open=_parse_bool(row.get("is_open", "true")),
                    prev_open_date=(
                        date.fromisoformat(row["prev_open_date"])
                        if row.get("prev_open_date")
                        else None
                    ),
                    next_open_date=(
                        date.fromisoformat(row["next_open_date"])
                        if row.get("next_open_date")
                        else None
                    ),
                )
            )
    return entries


def load_security_master_from_csv(path: Path) -> list[SecurityMasterRecord]:
    """Load security-master entries from a canonical CSV file."""
    records: list[SecurityMasterRecord] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                SecurityMasterRecord(
                    symbol=row["symbol"],
                    name=str(row.get("name", "")),
                    board=str(row.get("board", "")),
                    exchange=str(row.get("exchange", "")),
                    list_date=(
                        date.fromisoformat(row["list_date"])
                        if row.get("list_date")
                        else None
                    ),
                    delist_date=(
                        date.fromisoformat(row["delist_date"])
                        if row.get("delist_date")
                        else None
                    ),
                )
            )
    return records


def load_sector_mapping_from_csv(path: Path) -> list[SectorMappingRecord]:
    """Load daily sector mappings from a canonical CSV file."""
    records: list[SectorMappingRecord] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                SectorMappingRecord(
                    trade_date=date.fromisoformat(row["trade_date"]),
                    symbol=row["symbol"],
                    sector_id=row["sector_id"],
                    sector_name=row["sector_name"],
                    mapping_source=str(row.get("mapping_source", "")),
                    mapping_version=str(row.get("mapping_version", "")),
                )
            )
    return records


def load_concept_mapping_from_csv(path: Path) -> list[ConceptMappingRecord]:
    """Load daily concept mappings from a canonical CSV file."""
    records: list[ConceptMappingRecord] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            records.append(
                ConceptMappingRecord(
                    trade_date=date.fromisoformat(row["trade_date"]),
                    symbol=row["symbol"],
                    concept_id=row["concept_id"],
                    concept_name=row["concept_name"],
                    mapping_source=str(row.get("mapping_source", "")),
                    mapping_version=str(row.get("mapping_version", "")),
                    is_primary_concept=_parse_bool(row.get("is_primary_concept", "false")),
                    weight=float(row.get("weight", 0.0) or 0.0),
                )
            )
    return records
