from __future__ import annotations

import csv
import time
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FreeDataBootstrapConfig:
    start_date: date
    end_date: date
    stock_symbols: list[str]
    index_symbols: list[str]
    adjust: str
    pause_seconds: float
    raw_dir: Path
    reference_dir: Path
    daily_bars_filename: str
    index_daily_bars_filename: str
    trading_calendar_filename: str
    security_master_filename: str
    adjustment_factors_filename: str

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "FreeDataBootstrapConfig":
        time_range = config["time_range"]
        paths = config["paths"]
        outputs = config["outputs"]
        provider = config.get("provider", {})
        universe = config["universe"]
        stock_symbols = _merge_symbol_sources(
            inline_symbols=[str(symbol) for symbol in universe.get("stock_symbols", [])],
            file_path=Path(universe["stock_symbols_file"]) if universe.get("stock_symbols_file") else None,
        )
        index_symbols = _merge_symbol_sources(
            inline_symbols=[str(symbol) for symbol in universe.get("index_symbols", [])],
            file_path=Path(universe["index_symbols_file"]) if universe.get("index_symbols_file") else None,
        )
        return cls(
            start_date=date.fromisoformat(str(time_range["start_date"])),
            end_date=date.fromisoformat(str(time_range["end_date"])),
            stock_symbols=stock_symbols,
            index_symbols=index_symbols,
            adjust=str(provider.get("adjust", "qfq")),
            pause_seconds=float(provider.get("pause_seconds", 0.2)),
            raw_dir=Path(paths["raw_dir"]),
            reference_dir=Path(paths["reference_dir"]),
            daily_bars_filename=str(outputs["daily_bars_filename"]),
            index_daily_bars_filename=str(outputs["index_daily_bars_filename"]),
            trading_calendar_filename=str(outputs["trading_calendar_filename"]),
            security_master_filename=str(outputs["security_master_filename"]),
            adjustment_factors_filename=str(outputs["adjustment_factors_filename"]),
        )


def _require_akshare() -> Any:
    try:
        import akshare as ak
    except ImportError as exc:
        raise RuntimeError(
            "AKShare is not installed. Run `python -m pip install -e .[free-data]` first."
        ) from exc
    return ak


def _format_ymd(value: date) -> str:
    return value.strftime("%Y%m%d")


def _load_symbol_list(path: Path) -> list[str]:
    symbols: list[str] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            value = line.strip()
            if not value or value.startswith("#"):
                continue
            symbol = value.split(",", 1)[0].strip().strip("\"'").zfill(6)
            if symbol:
                symbols.append(symbol)
    return symbols


def _merge_symbol_sources(
    *,
    inline_symbols: list[str],
    file_path: Path | None,
) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for source_symbol in inline_symbols + (_load_symbol_list(file_path) if file_path is not None else []):
        symbol = str(source_symbol).strip().strip("\"'").zfill(6)
        if not symbol or symbol in seen:
            continue
        ordered.append(symbol)
        seen.add(symbol)
    return ordered


def _parse_cn_date(value: Any) -> date:
    text = str(value).strip()
    if " " in text:
        text = text.split(" ", 1)[0]
    if "-" in text:
        return date.fromisoformat(text)
    return datetime.strptime(text, "%Y%m%d").date()


def _infer_exchange(symbol: str) -> str:
    if symbol.startswith(("600", "601", "603", "605", "688", "689", "730")):
        return "SSE"
    if symbol.startswith(("000", "001", "002", "003", "300", "301")):
        return "SZSE"
    if symbol.startswith(("430", "830", "831", "832", "833", "835", "836", "837", "838", "839", "870", "871", "872", "873", "920")):
        return "BSE"
    return "UNKNOWN"


def _infer_board(symbol: str) -> str:
    if symbol.startswith(("688", "689")):
        return "STAR"
    if symbol.startswith(("300", "301")):
        return "ChiNext"
    if symbol.startswith(("830", "831", "832", "833", "835", "836", "837", "838", "839", "870", "871", "872", "873", "920", "430")):
        return "BSE"
    if symbol.startswith(("000", "001", "002", "003", "600", "601", "603", "605")):
        return "Main"
    return "Unknown"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> Path:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


class AkshareFreeDataBootstrapper:
    """Bootstrap a minimum free dataset pack into canonical repo directories."""

    def __init__(self, config: FreeDataBootstrapConfig) -> None:
        self.config = config
        self.ak = _require_akshare()
        self._security_details_cache: dict[str, dict[str, str]] = {}
        self._adjustment_factor_cache: dict[str, dict[date, float]] = {}
        self._trade_dates_cache: list[date] | None = None

    def run(self) -> dict[str, Path]:
        outputs = {
            "adjustment_factors": self.export_adjustment_factors(),
            "daily_bars": self.export_daily_bars(),
            "index_daily_bars": self.export_index_daily_bars(),
            "trading_calendar": self.export_trading_calendar(),
            "security_master_lite": self.export_security_master_lite(),
        }
        return outputs

    def export_daily_bars(self) -> Path:
        rows: list[dict[str, Any]] = []
        security_details_by_symbol = {
            symbol: self._fetch_security_master_details(symbol)
            for symbol in self.config.stock_symbols
        }
        for symbol in self.config.stock_symbols:
            list_date = self._parse_iso_date(
                security_details_by_symbol.get(symbol, {}).get("list_date", "")
            )
            adjustment_factors = self._fetch_adjustment_factors(symbol)
            frame = self.ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=_format_ymd(self.config.start_date),
                end_date=_format_ymd(self.config.end_date),
                adjust=self.config.adjust,
            )
            if frame.empty:
                continue
            previous_close: float | None = None
            for record in frame.to_dict(orient="records"):
                trade_date = _parse_cn_date(record["日期"])
                close = float(record["收盘"])
                rows.append(
                    {
                        "trade_date": trade_date.isoformat(),
                        "symbol": symbol,
                        "open": float(record["开盘"]),
                        "high": float(record["最高"]),
                        "low": float(record["最低"]),
                        "close": close,
                        "volume": float(record["成交量"]),
                        "turnover": float(record["成交额"]),
                        "pre_close": previous_close if previous_close is not None else close,
                        "adjust_factor": adjustment_factors.get(trade_date, 1.0),
                        "is_st": "false",
                        "is_suspended": "false",
                        "listed_days": self._approx_listed_days(list_date, trade_date),
                    }
                )
                previous_close = close
            time.sleep(self.config.pause_seconds)

        output_path = (
            self.config.raw_dir
            / "daily_bars"
            / self.config.daily_bars_filename
        )
        return _write_csv(
            output_path,
            [
                "trade_date",
                "symbol",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "turnover",
                "pre_close",
                "adjust_factor",
                "is_st",
                "is_suspended",
                "listed_days",
            ],
            rows,
        )

    def export_adjustment_factors(self) -> Path:
        rows: list[dict[str, Any]] = []
        for symbol in self.config.stock_symbols:
            factors = self._fetch_adjustment_factors(symbol)
            for trade_date, adjust_factor in sorted(factors.items()):
                rows.append(
                    {
                        "trade_date": trade_date.isoformat(),
                        "symbol": symbol,
                        "adjust_factor": round(adjust_factor, 12),
                    }
                )

        output_path = (
            self.config.reference_dir
            / "adjustment_factors"
            / self.config.adjustment_factors_filename
        )
        return _write_csv(
            output_path,
            ["trade_date", "symbol", "adjust_factor"],
            rows,
        )

    def export_index_daily_bars(self) -> Path:
        rows: list[dict[str, Any]] = []
        for symbol in self.config.index_symbols:
            frame = self.ak.index_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=_format_ymd(self.config.start_date),
                end_date=_format_ymd(self.config.end_date),
            )
            if frame.empty:
                continue
            previous_close: float | None = None
            for record in frame.to_dict(orient="records"):
                trade_date = _parse_cn_date(record["日期"])
                close = float(record["收盘"])
                rows.append(
                    {
                        "trade_date": trade_date.isoformat(),
                        "symbol": symbol,
                        "open": float(record["开盘"]),
                        "high": float(record["最高"]),
                        "low": float(record["最低"]),
                        "close": close,
                        "volume": float(record["成交量"]),
                        "turnover": float(record["成交额"]),
                        "pre_close": previous_close if previous_close is not None else close,
                    }
                )
                previous_close = close
            time.sleep(self.config.pause_seconds)

        output_path = (
            self.config.raw_dir
            / "index_daily_bars"
            / self.config.index_daily_bars_filename
        )
        return _write_csv(
            output_path,
            [
                "trade_date",
                "symbol",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "turnover",
                "pre_close",
            ],
            rows,
        )

    def export_trading_calendar(self) -> Path:
        frame = self.ak.tool_trade_date_hist_sina()
        calendar_dates = sorted(
            _parse_cn_date(value)
            for value in frame.iloc[:, 0].tolist()
            if self.config.start_date <= _parse_cn_date(value) <= self.config.end_date
        )
        rows: list[dict[str, Any]] = []
        for idx, trade_day in enumerate(calendar_dates):
            prev_open_date = calendar_dates[idx - 1].isoformat() if idx > 0 else ""
            next_open_date = (
                calendar_dates[idx + 1].isoformat()
                if idx + 1 < len(calendar_dates)
                else ""
            )
            rows.append(
                {
                    "trade_date": trade_day.isoformat(),
                    "is_open": "true",
                    "prev_open_date": prev_open_date,
                    "next_open_date": next_open_date,
                }
            )

        output_path = (
            self.config.reference_dir
            / "trading_calendar"
            / self.config.trading_calendar_filename
        )
        return _write_csv(
            output_path,
            ["trade_date", "is_open", "prev_open_date", "next_open_date"],
            rows,
        )

    def export_security_master_lite(self) -> Path:
        rows_by_symbol: dict[str, dict[str, Any]] = {}
        try:
            frame = self.ak.stock_info_a_code_name()
            for record in frame.to_dict(orient="records"):
                symbol = str(record["code"]).zfill(6)
                rows_by_symbol[symbol] = {
                    "symbol": symbol,
                    "name": str(record["name"]),
                    "board": _infer_board(symbol),
                    "exchange": _infer_exchange(symbol),
                    "list_date": "",
                    "delist_date": "",
                }
        except Exception as exc:
            # Free-source bootstrap should degrade gracefully instead of blocking
            # the whole data onboarding path on one slow reference endpoint.
            print(
                "Warning: full security master bootstrap failed; "
                f"falling back to configured stock symbols only. Error: {exc}"
            )
            for symbol in sorted(set(self.config.stock_symbols)):
                rows_by_symbol[symbol] = {
                    "symbol": symbol,
                    "name": "",
                    "board": _infer_board(symbol),
                    "exchange": _infer_exchange(symbol),
                    "list_date": "",
                    "delist_date": "",
                }

        for symbol in sorted(set(self.config.stock_symbols)):
            enriched = self._fetch_security_master_details(symbol)
            base_row = rows_by_symbol.setdefault(
                symbol,
                {
                    "symbol": symbol,
                    "name": "",
                    "board": _infer_board(symbol),
                    "exchange": _infer_exchange(symbol),
                    "list_date": "",
                    "delist_date": "",
                },
            )
            for key, value in enriched.items():
                if value not in {"", None}:
                    base_row[key] = value
            time.sleep(self.config.pause_seconds)

        rows = [rows_by_symbol[symbol] for symbol in sorted(rows_by_symbol)]

        output_path = (
            self.config.reference_dir
            / "security_master"
            / self.config.security_master_filename
        )
        return _write_csv(
            output_path,
            ["symbol", "name", "board", "exchange", "list_date", "delist_date"],
            rows,
        )

    def _fetch_security_master_details(self, symbol: str) -> dict[str, str]:
        if symbol in self._security_details_cache:
            return self._security_details_cache[symbol]
        try:
            frame = self.ak.stock_individual_info_em(symbol=symbol)
        except Exception:
            return {}

        lookup = {
            str(record["item"]).strip(): str(record["value"]).strip()
            for record in frame.to_dict(orient="records")
        }
        list_date_raw = lookup.get("上市时间", "")
        list_date = ""
        if list_date_raw and list_date_raw.isdigit() and len(list_date_raw) == 8:
            list_date = datetime.strptime(list_date_raw, "%Y%m%d").date().isoformat()

        details = {
            "name": lookup.get("股票简称", ""),
            "list_date": list_date,
            "delist_date": "",
        }
        self._security_details_cache[symbol] = details
        return details

    def _fetch_adjustment_factors(self, symbol: str) -> dict[date, float]:
        if symbol in self._adjustment_factor_cache:
            return self._adjustment_factor_cache[symbol]

        try:
            frame = self.ak.stock_zh_a_daily(
                symbol=self._symbol_with_exchange_prefix(symbol),
                adjust="qfq-factor",
            )
        except Exception:
            factors = self._default_adjustment_factors()
            self._adjustment_factor_cache[symbol] = factors
            return factors

        factor_events = sorted(
            (
                _parse_cn_date(record["date"]),
                float(record["qfq_factor"]),
            )
            for record in frame.to_dict(orient="records")
        )
        if not factor_events:
            factors = self._default_adjustment_factors()
            self._adjustment_factor_cache[symbol] = factors
            return factors

        event_index = 0
        current_factor = factor_events[0][1]
        factors: dict[date, float] = {}
        for trade_date in self._trade_dates_in_range():
            while (
                event_index + 1 < len(factor_events)
                and factor_events[event_index + 1][0] <= trade_date
            ):
                event_index += 1
                current_factor = factor_events[event_index][1]
            factors[trade_date] = current_factor

        self._adjustment_factor_cache[symbol] = factors
        return factors

    def _trade_dates_in_range(self) -> list[date]:
        if self._trade_dates_cache is not None:
            return self._trade_dates_cache
        calendar = self.ak.tool_trade_date_hist_sina()
        self._trade_dates_cache = sorted(
            _parse_cn_date(value)
            for value in calendar.iloc[:, 0].tolist()
            if self.config.start_date <= _parse_cn_date(value) <= self.config.end_date
        )
        return self._trade_dates_cache

    def _default_adjustment_factors(self) -> dict[date, float]:
        return {trade_date: 1.0 for trade_date in self._trade_dates_in_range()}

    def _symbol_with_exchange_prefix(self, symbol: str) -> str:
        exchange = _infer_exchange(symbol)
        if exchange == "SSE":
            return f"sh{symbol}"
        if exchange == "SZSE":
            return f"sz{symbol}"
        if exchange == "BSE":
            return f"bj{symbol}"
        return symbol

    def _parse_iso_date(self, value: str) -> date | None:
        text = str(value).strip()
        if not text:
            return None
        return date.fromisoformat(text)

    def _approx_listed_days(self, list_date: date | None, trade_date: date) -> int:
        if list_date is None:
            return 0
        return max((trade_date - list_date).days, 0)
