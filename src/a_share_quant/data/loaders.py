from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from a_share_quant.common.models import (
    DailyBar,
    MainlineWindow,
    SectorSnapshot,
    Signal,
    StockSnapshot,
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
