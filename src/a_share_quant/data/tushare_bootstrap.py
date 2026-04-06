from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.data.tushare_client import build_tushare_pro


def _format_ymd(value: date) -> str:
    return value.strftime("%Y%m%d")


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> Path:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _load_cpo_symbols_from_report(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = payload.get("object_role_time_rows", [])
    symbols: list[str] = []
    seen: set[str] = set()
    for row in rows:
        symbol = str(row.get("symbol", "")).strip()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        symbols.append(symbol)
    if not symbols:
        raise ValueError(f"No symbols found in cohort report: {path}")
    return symbols


def _load_symbols_from_csv(path: Path, *, field: str = "symbol") -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    symbols: list[str] = []
    seen: set[str] = set()
    for row in rows:
        symbol = str(row.get(field, "")).strip()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        symbols.append(symbol)
    if not symbols:
        raise ValueError(f"No symbols found in csv: {path}")
    return symbols


def _symbol_to_ts_code(symbol: str) -> str:
    if symbol.startswith(("600", "601", "603", "605", "688", "689", "730")):
        return f"{symbol}.SH"
    if symbol.startswith(("000", "001", "002", "003", "300", "301")):
        return f"{symbol}.SZ"
    if symbol.startswith(("430", "830", "831", "832", "833", "835", "836", "837", "838", "839", "870", "871", "872", "873", "920")):
        return f"{symbol}.BJ"
    return symbol


@dataclass(slots=True)
class TushareCpoBootstrapConfig:
    start_date: date
    end_date: date
    cohort_report_path: Path
    raw_dir: Path
    reference_dir: Path
    pause_seconds: float
    daily_basic_filename: str
    moneyflow_filename: str
    stk_limit_filename: str

    @property
    def symbols(self) -> list[str]:
        return _load_cpo_symbols_from_report(self.cohort_report_path)


class TushareCpoBootstrapper:
    def __init__(self, config: TushareCpoBootstrapConfig, *, repo_root: Path) -> None:
        self.config = config
        self.repo_root = repo_root
        self.pro = build_tushare_pro(repo_root=repo_root)

    def run(self) -> dict[str, Any]:
        daily_basic_rows = self.fetch_daily_basic_rows()
        moneyflow_rows = self.fetch_moneyflow_rows()
        stk_limit_rows = self.fetch_stk_limit_rows()

        daily_basic_path = _write_csv(
            self.config.reference_dir / "tushare_daily_basic" / self.config.daily_basic_filename,
            [
                "trade_date",
                "symbol",
                "ts_code",
                "turnover_rate",
                "turnover_rate_f",
                "volume_ratio",
                "pe",
                "pb",
                "ps",
                "total_share",
                "float_share",
                "free_share",
                "total_mv",
                "circ_mv",
            ],
            daily_basic_rows,
        )
        moneyflow_path = _write_csv(
            self.config.raw_dir / "moneyflow" / self.config.moneyflow_filename,
            list(moneyflow_rows[0].keys()) if moneyflow_rows else [
                "trade_date","symbol","ts_code","buy_sm_vol","buy_sm_amount","sell_sm_vol","sell_sm_amount",
                "buy_md_vol","buy_md_amount","sell_md_vol","sell_md_amount","buy_lg_vol","buy_lg_amount",
                "sell_lg_vol","sell_lg_amount","buy_elg_vol","buy_elg_amount","sell_elg_vol","sell_elg_amount",
                "net_mf_vol","net_mf_amount"
            ],
            moneyflow_rows,
        )
        stk_limit_path = _write_csv(
            self.config.reference_dir / "stk_limit" / self.config.stk_limit_filename,
            list(stk_limit_rows[0].keys()) if stk_limit_rows else ["trade_date","symbol","ts_code","pre_close","up_limit","down_limit"],
            stk_limit_rows,
        )
        return {
            "symbols": self.config.symbols,
            "daily_basic_path": daily_basic_path,
            "moneyflow_path": moneyflow_path,
            "stk_limit_path": stk_limit_path,
            "daily_basic_rows": len(daily_basic_rows),
            "moneyflow_rows": len(moneyflow_rows),
            "stk_limit_rows": len(stk_limit_rows),
        }

    def fetch_daily_basic_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for symbol in self.config.symbols:
            ts_code = _symbol_to_ts_code(symbol)
            frame = self.pro.daily_basic(
                ts_code=ts_code,
                start_date=_format_ymd(self.config.start_date),
                end_date=_format_ymd(self.config.end_date),
                fields="ts_code,trade_date,turnover_rate,turnover_rate_f,volume_ratio,pe,pb,ps,total_share,float_share,free_share,total_mv,circ_mv",
            )
            if frame is None or frame.empty:
                time.sleep(self.config.pause_seconds)
                continue
            for record in frame.to_dict(orient="records"):
                rows.append(
                    {
                        "trade_date": str(record.get("trade_date", "")),
                        "symbol": symbol,
                        "ts_code": ts_code,
                        "turnover_rate": record.get("turnover_rate"),
                        "turnover_rate_f": record.get("turnover_rate_f"),
                        "volume_ratio": record.get("volume_ratio"),
                        "pe": record.get("pe"),
                        "pb": record.get("pb"),
                        "ps": record.get("ps"),
                        "total_share": record.get("total_share"),
                        "float_share": record.get("float_share"),
                        "free_share": record.get("free_share"),
                        "total_mv": record.get("total_mv"),
                        "circ_mv": record.get("circ_mv"),
                    }
                )
            time.sleep(self.config.pause_seconds)
        return rows

    def fetch_moneyflow_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for symbol in self.config.symbols:
            ts_code = _symbol_to_ts_code(symbol)
            frame = self.pro.moneyflow(
                ts_code=ts_code,
                start_date=_format_ymd(self.config.start_date),
                end_date=_format_ymd(self.config.end_date),
            )
            if frame is None or frame.empty:
                time.sleep(self.config.pause_seconds)
                continue
            for record in frame.to_dict(orient="records"):
                row = {"trade_date": str(record.get("trade_date", "")), "symbol": symbol, "ts_code": ts_code}
                for key, value in record.items():
                    if key in {"trade_date", "ts_code"}:
                        continue
                    row[key] = value
                rows.append(row)
            time.sleep(self.config.pause_seconds)
        return rows

    def fetch_stk_limit_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for symbol in self.config.symbols:
            ts_code = _symbol_to_ts_code(symbol)
            frame = self.pro.stk_limit(
                ts_code=ts_code,
                start_date=_format_ymd(self.config.start_date),
                end_date=_format_ymd(self.config.end_date),
            )
            if frame is None or frame.empty:
                time.sleep(self.config.pause_seconds)
                continue
            for record in frame.to_dict(orient="records"):
                rows.append(
                    {
                        "trade_date": str(record.get("trade_date", "")),
                        "symbol": symbol,
                        "ts_code": ts_code,
                        "pre_close": record.get("pre_close"),
                        "up_limit": record.get("up_limit"),
                        "down_limit": record.get("down_limit"),
                    }
                )
            time.sleep(self.config.pause_seconds)
        return rows


@dataclass(slots=True)
class TushareUniverseBootstrapConfig:
    start_date: date
    end_date: date
    universe_csv_path: Path
    raw_dir: Path
    reference_dir: Path
    pause_seconds: float
    daily_filename: str
    daily_basic_filename: str
    moneyflow_filename: str
    stk_limit_filename: str
    symbol_field: str = "symbol"

    @property
    def symbols(self) -> list[str]:
        return _load_symbols_from_csv(self.universe_csv_path, field=self.symbol_field)


class TushareUniverseBootstrapper:
    def __init__(self, config: TushareUniverseBootstrapConfig, *, repo_root: Path) -> None:
        self.config = config
        self.repo_root = repo_root
        self.pro = build_tushare_pro(repo_root=repo_root)

    def run(self) -> dict[str, Any]:
        daily_rows = self.fetch_daily_rows()
        daily_basic_rows = self.fetch_daily_basic_rows()
        moneyflow_rows = self.fetch_moneyflow_rows()
        stk_limit_rows = self.fetch_stk_limit_rows()

        daily_path = _write_csv(
            self.config.raw_dir / "daily_bars" / self.config.daily_filename,
            [
                "trade_date",
                "symbol",
                "ts_code",
                "open",
                "high",
                "low",
                "close",
                "pre_close",
                "change",
                "pct_chg",
                "volume",
                "amount",
            ],
            daily_rows,
        )
        daily_basic_path = _write_csv(
            self.config.reference_dir / "tushare_daily_basic" / self.config.daily_basic_filename,
            [
                "trade_date",
                "symbol",
                "ts_code",
                "turnover_rate",
                "turnover_rate_f",
                "volume_ratio",
                "pe",
                "pb",
                "ps",
                "total_share",
                "float_share",
                "free_share",
                "total_mv",
                "circ_mv",
            ],
            daily_basic_rows,
        )
        moneyflow_path = _write_csv(
            self.config.raw_dir / "moneyflow" / self.config.moneyflow_filename,
            list(moneyflow_rows[0].keys()) if moneyflow_rows else [
                "trade_date","symbol","ts_code","buy_sm_vol","buy_sm_amount","sell_sm_vol","sell_sm_amount",
                "buy_md_vol","buy_md_amount","sell_md_vol","sell_md_amount","buy_lg_vol","buy_lg_amount",
                "sell_lg_vol","sell_lg_amount","buy_elg_vol","buy_elg_amount","sell_elg_vol","sell_elg_amount",
                "net_mf_vol","net_mf_amount"
            ],
            moneyflow_rows,
        )
        stk_limit_path = _write_csv(
            self.config.reference_dir / "stk_limit" / self.config.stk_limit_filename,
            list(stk_limit_rows[0].keys()) if stk_limit_rows else ["trade_date","symbol","ts_code","pre_close","up_limit","down_limit"],
            stk_limit_rows,
        )
        return {
            "symbols": self.config.symbols,
            "daily_path": daily_path,
            "daily_basic_path": daily_basic_path,
            "moneyflow_path": moneyflow_path,
            "stk_limit_path": stk_limit_path,
            "daily_rows": len(daily_rows),
            "daily_basic_rows": len(daily_basic_rows),
            "moneyflow_rows": len(moneyflow_rows),
            "stk_limit_rows": len(stk_limit_rows),
        }

    def fetch_daily_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for symbol in self.config.symbols:
            ts_code = _symbol_to_ts_code(symbol)
            frame = self.pro.daily(
                ts_code=ts_code,
                start_date=_format_ymd(self.config.start_date),
                end_date=_format_ymd(self.config.end_date),
            )
            if frame is None or frame.empty:
                time.sleep(self.config.pause_seconds)
                continue
            for record in frame.to_dict(orient="records"):
                rows.append(
                    {
                        "trade_date": str(record.get("trade_date", "")),
                        "symbol": symbol,
                        "ts_code": ts_code,
                        "open": record.get("open"),
                        "high": record.get("high"),
                        "low": record.get("low"),
                        "close": record.get("close"),
                        "pre_close": record.get("pre_close"),
                        "change": record.get("change"),
                        "pct_chg": record.get("pct_chg"),
                        "volume": record.get("vol"),
                        "amount": record.get("amount"),
                    }
                )
            time.sleep(self.config.pause_seconds)
        return rows

    def fetch_daily_basic_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for symbol in self.config.symbols:
            ts_code = _symbol_to_ts_code(symbol)
            frame = self.pro.daily_basic(
                ts_code=ts_code,
                start_date=_format_ymd(self.config.start_date),
                end_date=_format_ymd(self.config.end_date),
                fields="ts_code,trade_date,turnover_rate,turnover_rate_f,volume_ratio,pe,pb,ps,total_share,float_share,free_share,total_mv,circ_mv",
            )
            if frame is None or frame.empty:
                time.sleep(self.config.pause_seconds)
                continue
            for record in frame.to_dict(orient="records"):
                rows.append(
                    {
                        "trade_date": str(record.get("trade_date", "")),
                        "symbol": symbol,
                        "ts_code": ts_code,
                        "turnover_rate": record.get("turnover_rate"),
                        "turnover_rate_f": record.get("turnover_rate_f"),
                        "volume_ratio": record.get("volume_ratio"),
                        "pe": record.get("pe"),
                        "pb": record.get("pb"),
                        "ps": record.get("ps"),
                        "total_share": record.get("total_share"),
                        "float_share": record.get("float_share"),
                        "free_share": record.get("free_share"),
                        "total_mv": record.get("total_mv"),
                        "circ_mv": record.get("circ_mv"),
                    }
                )
            time.sleep(self.config.pause_seconds)
        return rows

    def fetch_moneyflow_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for symbol in self.config.symbols:
            ts_code = _symbol_to_ts_code(symbol)
            frame = self.pro.moneyflow(
                ts_code=ts_code,
                start_date=_format_ymd(self.config.start_date),
                end_date=_format_ymd(self.config.end_date),
            )
            if frame is None or frame.empty:
                time.sleep(self.config.pause_seconds)
                continue
            for record in frame.to_dict(orient="records"):
                row = {"trade_date": str(record.get("trade_date", "")), "symbol": symbol, "ts_code": ts_code}
                for key, value in record.items():
                    if key in {"trade_date", "ts_code"}:
                        continue
                    row[key] = value
                rows.append(row)
            time.sleep(self.config.pause_seconds)
        return rows

    def fetch_stk_limit_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for symbol in self.config.symbols:
            ts_code = _symbol_to_ts_code(symbol)
            frame = self.pro.stk_limit(
                ts_code=ts_code,
                start_date=_format_ymd(self.config.start_date),
                end_date=_format_ymd(self.config.end_date),
            )
            if frame is None or frame.empty:
                time.sleep(self.config.pause_seconds)
                continue
            for record in frame.to_dict(orient="records"):
                rows.append(
                    {
                        "trade_date": str(record.get("trade_date", "")),
                        "symbol": symbol,
                        "ts_code": ts_code,
                        "pre_close": record.get("pre_close"),
                        "up_limit": record.get("up_limit"),
                        "down_limit": record.get("down_limit"),
                    }
                )
            time.sleep(self.config.pause_seconds)
        return rows
