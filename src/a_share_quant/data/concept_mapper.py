from __future__ import annotations

import csv
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import requests

from a_share_quant.common.models import ConceptMappingRecord, DailyBar


def _require_akshare() -> Any:
    try:
        import akshare as ak
    except ImportError as exc:
        raise RuntimeError(
            "AKShare is not installed. Run `python -m pip install -e .[free-data]` first."
        ) from exc
    return ak


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> Path:
    _ensure_parent(path)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


@dataclass(slots=True)
class ConceptMapperConfig:
    mapping_source: str
    mapping_version: str
    output_csv: Path
    max_boards_to_scan: int
    min_concepts_per_symbol: int
    max_concepts_per_symbol: int
    board_pause_seconds: float
    use_board_history: bool
    history_period: str
    history_adjust: str
    history_start_date: str | None
    history_end_date: str | None
    min_export_weight: float
    base_rank_weight: float
    board_history_weight: float
    stock_alignment_weight: float

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "ConceptMapperConfig":
        return cls(
            mapping_source=str(config.get("mapping_source", "akshare_em_concept")),
            mapping_version=str(config.get("mapping_version", "concept_bootstrap_v1")),
            output_csv=Path(config["output_csv"]),
            max_boards_to_scan=int(config.get("max_boards_to_scan", 80)),
            min_concepts_per_symbol=int(config.get("min_concepts_per_symbol", 1)),
            max_concepts_per_symbol=int(config.get("max_concepts_per_symbol", 3)),
            board_pause_seconds=float(config.get("board_pause_seconds", 0.0)),
            use_board_history=bool(config.get("use_board_history", True)),
            history_period=str(config.get("history_period", "daily")),
            history_adjust=str(config.get("history_adjust", "")),
            history_start_date=(
                str(config["history_start_date"])
                if config.get("history_start_date")
                else None
            ),
            history_end_date=(
                str(config["history_end_date"])
                if config.get("history_end_date")
                else None
            ),
            min_export_weight=float(config.get("min_export_weight", 0.12)),
            base_rank_weight=float(config.get("base_rank_weight", 0.25)),
            board_history_weight=float(config.get("board_history_weight", 0.50)),
            stock_alignment_weight=float(config.get("stock_alignment_weight", 0.25)),
        )


class AkshareConceptMapper:
    """Resolve a daily concept mapping with optional concept-history-aware primary rotation."""

    def __init__(self, config: ConceptMapperConfig) -> None:
        self.config = config
        self.ak = _require_akshare()

    def build_daily_mapping(self, bars: list[DailyBar]) -> list[ConceptMappingRecord]:
        bars_by_symbol: dict[str, list[DailyBar]] = {}
        for bar in sorted(bars, key=lambda item: (item.symbol, item.trade_date)):
            bars_by_symbol.setdefault(bar.symbol, []).append(bar)

        target_symbols = set(bars_by_symbol)
        concept_hits_by_symbol: dict[str, list[dict[str, Any]]] = {
            symbol: [] for symbol in target_symbols
        }
        matched_boards: dict[str, dict[str, Any]] = {}

        board_rows = self.ak.stock_board_concept_name_em().to_dict(orient="records")
        board_name_key = self._resolve_key(board_rows, ["板块名称", "鏉垮潡鍚嶇О"])
        board_code_key = self._resolve_key(board_rows, ["板块代码", "鏉垮潡浠ｇ爜"])
        board_rank_key = self._resolve_key(board_rows, ["排名", "鎺掑悕"])

        boards_scanned = 0
        for board_row in board_rows:
            if boards_scanned >= self.config.max_boards_to_scan:
                break
            if all(
                len(concept_hits_by_symbol[symbol]) >= self.config.min_concepts_per_symbol
                for symbol in target_symbols
            ):
                break

            board_name = str(board_row[board_name_key]).strip()
            board_code = str(board_row[board_code_key]).strip()
            if not board_name or not board_code:
                continue
            try:
                board_rank = int(float(board_row[board_rank_key]))
            except (TypeError, ValueError):
                continue

            try:
                constituent_rows = self.ak.stock_board_concept_cons_em(symbol=board_name).to_dict(
                    orient="records"
                )
            except Exception:
                continue

            boards_scanned += 1
            if self.config.board_pause_seconds > 0:
                time.sleep(self.config.board_pause_seconds)

            code_key = self._resolve_key(constituent_rows, ["代码", "浠ｇ爜"])
            constituents = {
                str(row[code_key]).zfill(6)
                for row in constituent_rows
            }
            matched_symbols = sorted(target_symbols & constituents)
            if not matched_symbols:
                continue

            matched_boards[board_code] = {
                "concept_id": board_code,
                "concept_name": board_name,
                "board_rank": board_rank,
            }
            for symbol in matched_symbols:
                if len(concept_hits_by_symbol[symbol]) >= self.config.max_concepts_per_symbol:
                    continue
                existing_ids = {
                    str(item["concept_id"]) for item in concept_hits_by_symbol[symbol]
                }
                if board_code in existing_ids:
                    continue
                concept_hits_by_symbol[symbol].append(
                    {
                        "concept_id": board_code,
                        "concept_name": board_name,
                        "board_rank": board_rank,
                    }
                )

        concept_history = self._load_concept_history(
            matched_boards=matched_boards,
            bars_by_symbol=bars_by_symbol,
        )
        records: list[ConceptMappingRecord] = []
        for symbol, symbol_bars in bars_by_symbol.items():
            concept_hits = sorted(
                concept_hits_by_symbol.get(symbol, []),
                key=lambda item: item["board_rank"],
            )
            if not concept_hits:
                continue
            records.extend(
                self._build_symbol_records(
                    symbol=symbol,
                    symbol_bars=symbol_bars,
                    concept_hits=concept_hits,
                    concept_history=concept_history,
                )
            )
        return records

    def write_daily_mapping(self, records: list[ConceptMappingRecord]) -> Path:
        rows = [
            {
                "trade_date": record.trade_date.isoformat(),
                "symbol": record.symbol,
                "concept_id": record.concept_id,
                "concept_name": record.concept_name,
                "mapping_source": record.mapping_source,
                "mapping_version": record.mapping_version,
                "is_primary_concept": str(record.is_primary_concept).lower(),
                "weight": round(record.weight, 6),
            }
            for record in records
        ]
        return _write_csv(
            self.config.output_csv,
            [
                "trade_date",
                "symbol",
                "concept_id",
                "concept_name",
                "mapping_source",
                "mapping_version",
                "is_primary_concept",
                "weight",
            ],
            rows,
        )

    def _build_symbol_records(
        self,
        *,
        symbol: str,
        symbol_bars: list[DailyBar],
        concept_hits: list[dict[str, Any]],
        concept_history: dict[str, dict[date, dict[str, float]]],
    ) -> list[ConceptMappingRecord]:
        records: list[ConceptMappingRecord] = []
        for bar in symbol_bars:
            weights = self._weights_for_hits_on_date(
                bar=bar,
                symbol_bars=symbol_bars,
                concept_hits=concept_hits,
                concept_history=concept_history,
            )
            if not weights:
                continue
            primary_index = max(range(len(weights)), key=weights.__getitem__)
            for index, hit in enumerate(concept_hits):
                weight = weights[index]
                if index != primary_index and weight < self.config.min_export_weight:
                    continue
                records.append(
                    ConceptMappingRecord(
                        trade_date=bar.trade_date,
                        symbol=symbol,
                        concept_id=str(hit["concept_id"]),
                        concept_name=str(hit["concept_name"]),
                        mapping_source=self.config.mapping_source,
                        mapping_version=self.config.mapping_version,
                        is_primary_concept=index == primary_index,
                        weight=round(weight, 6),
                    )
                )
        return records

    def _weights_for_hits(self, concept_hits: list[dict[str, Any]]) -> list[float]:
        raw_weights = [1.0 / float(index + 1) for index in range(len(concept_hits))]
        total = sum(raw_weights) or 1.0
        return [weight / total for weight in raw_weights]

    def _weights_for_hits_on_date(
        self,
        *,
        bar: DailyBar,
        symbol_bars: list[DailyBar],
        concept_hits: list[dict[str, Any]],
        concept_history: dict[str, dict[date, dict[str, float]]],
    ) -> list[float]:
        if not concept_hits:
            return []
        if len(concept_hits) == 1:
            return [1.0]

        fallback_weights = self._weights_for_hits(concept_hits)
        if not self.config.use_board_history:
            return fallback_weights

        stock_daily_return = ((bar.close / bar.pre_close) - 1.0) if bar.pre_close > 0 else 0.0
        stock_trailing_return = self._symbol_trailing_return(symbol_bars, bar.trade_date)
        raw_weights: list[float] = []

        for index, hit in enumerate(concept_hits):
            base_rank_score = 1.0 / float(hit["board_rank"] + 1)
            history_point = concept_history.get(str(hit["concept_id"]), {}).get(bar.trade_date)
            if history_point is None:
                raw_weights.append(fallback_weights[index])
                continue

            stock_alignment = self._alignment_score(
                stock_daily_return=stock_daily_return,
                board_daily_return=history_point["daily_return"],
                stock_trailing_return=stock_trailing_return,
                board_trailing_return=history_point["trailing_return"],
            )
            raw_weights.append(
                (self.config.base_rank_weight * base_rank_score)
                + (self.config.board_history_weight * history_point["score"])
                + (self.config.stock_alignment_weight * stock_alignment)
            )

        total = sum(raw_weights) or 1.0
        return [weight / total for weight in raw_weights]

    def _alignment_score(
        self,
        *,
        stock_daily_return: float,
        board_daily_return: float,
        stock_trailing_return: float,
        board_trailing_return: float,
    ) -> float:
        daily_gap = abs(stock_daily_return - board_daily_return)
        trailing_gap = abs(stock_trailing_return - board_trailing_return)
        daily_alignment = max(0.0, 1.0 - (daily_gap / 0.08))
        trailing_alignment = max(0.0, 1.0 - (trailing_gap / 0.15))
        return (0.6 * daily_alignment) + (0.4 * trailing_alignment)

    def _symbol_trailing_return(
        self,
        symbol_bars: list[DailyBar],
        trade_date: date,
        window: int = 5,
    ) -> float:
        eligible = [candidate for candidate in symbol_bars if candidate.trade_date <= trade_date]
        recent = eligible[-window:]
        if len(recent) < 2 or recent[0].close <= 0:
            return 0.0
        return (recent[-1].close / recent[0].close) - 1.0

    def _load_concept_history(
        self,
        *,
        matched_boards: dict[str, dict[str, Any]],
        bars_by_symbol: dict[str, list[DailyBar]],
    ) -> dict[str, dict[date, dict[str, float]]]:
        if not self.config.use_board_history or not matched_boards:
            return {}

        all_trade_dates = [
            bar.trade_date
            for symbol_bars in bars_by_symbol.values()
            for bar in symbol_bars
        ]
        if not all_trade_dates:
            return {}
        start_date = self.config.history_start_date or min(all_trade_dates).strftime("%Y%m%d")
        end_date = self.config.history_end_date or max(all_trade_dates).strftime("%Y%m%d")

        history: dict[str, dict[date, dict[str, float]]] = {}
        for board_code in matched_boards:
            history[board_code] = self._fetch_board_history(
                board_code=board_code,
                start_date=start_date,
                end_date=end_date,
            )
        return history

    def _fetch_board_history(
        self,
        *,
        board_code: str,
        start_date: str,
        end_date: str,
    ) -> dict[date, dict[str, float]]:
        period_map = {"daily": "101", "weekly": "102", "monthly": "103"}
        adjust_map = {"": "0", "qfq": "1", "hfq": "2"}
        url = "https://91.push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": f"90.{board_code}",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": period_map.get(self.config.history_period, "101"),
            "fqt": adjust_map.get(self.config.history_adjust, "0"),
            "beg": start_date,
            "end": end_date,
            "smplmt": "10000",
            "lmt": "1000000",
        }
        try:
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return {}

        data = payload.get("data") or {}
        klines = data.get("klines") or []
        if not klines:
            return {}

        history: dict[date, dict[str, float]] = {}
        closes: list[float] = []
        for item in klines:
            fields = str(item).split(",")
            if len(fields) < 11:
                continue
            try:
                trade_date = date.fromisoformat(fields[0])
                close = float(fields[2])
                pct_change = float(fields[8])
                turnover = float(fields[10])
            except ValueError:
                continue
            closes.append(close)
            trailing_base = closes[-5] if len(closes) >= 5 else closes[0]
            trailing_return = (close / trailing_base) - 1.0 if trailing_base > 0 else 0.0
            history[trade_date] = {
                "score": self._board_score(
                    daily_return=pct_change / 100.0,
                    turnover=turnover,
                    trailing_return=trailing_return,
                ),
                "daily_return": pct_change / 100.0,
                "trailing_return": trailing_return,
            }
        return history

    def _board_score(
        self,
        *,
        daily_return: float,
        turnover: float,
        trailing_return: float,
    ) -> float:
        daily_strength = max(0.0, min(1.0, (daily_return + 0.05) / 0.10))
        trailing_strength = max(0.0, min(1.0, (trailing_return + 0.10) / 0.20))
        activity_strength = max(0.0, min(1.0, turnover / 8.0))
        return (0.45 * daily_strength) + (0.35 * trailing_strength) + (0.20 * activity_strength)

    def _resolve_key(self, rows: list[dict[str, Any]], candidates: list[str]) -> str:
        if not rows:
            raise ValueError("Cannot resolve columns from an empty row set.")
        sample_keys = list(rows[0].keys())
        for candidate in candidates:
            if candidate in sample_keys:
                return candidate
        raise KeyError(f"Could not resolve any of {candidates!r} from {sample_keys!r}")
