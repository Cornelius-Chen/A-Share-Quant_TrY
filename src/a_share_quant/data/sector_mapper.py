from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.common.models import DailyBar, SectorMappingRecord


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
class SectorMapperConfig:
    mapping_source: str
    mapping_version: str
    classification_field: str
    fallback_sector_name: str
    fallback_sector_id: str
    backfill_earliest_known: bool
    output_csv: Path

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "SectorMapperConfig":
        return cls(
            mapping_source=str(config.get("mapping_source", "akshare_cninfo")),
            mapping_version=str(config.get("mapping_version", "cninfo_bootstrap_v1")),
            classification_field=str(config.get("classification_field", "行业大类")),
            fallback_sector_name=str(config.get("fallback_sector_name", "UNKNOWN")),
            fallback_sector_id=str(config.get("fallback_sector_id", "UNKNOWN")),
            backfill_earliest_known=bool(config.get("backfill_earliest_known", True)),
            output_csv=Path(config["output_csv"]),
        )


class AkshareCninfoSectorMapper:
    """Resolve per-symbol daily sector mapping using CNInfo industry-change history."""

    def __init__(self, config: SectorMapperConfig) -> None:
        self.config = config
        self.ak = _require_akshare()

    def build_daily_mapping(self, bars: list[DailyBar]) -> list[SectorMappingRecord]:
        bars_by_symbol: dict[str, list[DailyBar]] = {}
        for bar in sorted(bars, key=lambda item: (item.symbol, item.trade_date)):
            bars_by_symbol.setdefault(bar.symbol, []).append(bar)

        records: list[SectorMappingRecord] = []
        for symbol, symbol_bars in bars_by_symbol.items():
            symbol_dates = [bar.trade_date for bar in symbol_bars]
            history = self._fetch_symbol_history(symbol, symbol_dates[0], symbol_dates[-1])
            records.extend(self._expand_history(symbol, symbol_dates, history))
        return records

    def write_daily_mapping(self, records: list[SectorMappingRecord]) -> Path:
        rows = [
            {
                "trade_date": record.trade_date.isoformat(),
                "symbol": record.symbol,
                "sector_id": record.sector_id,
                "sector_name": record.sector_name,
                "mapping_source": record.mapping_source,
                "mapping_version": record.mapping_version,
            }
            for record in records
        ]
        return _write_csv(
            self.config.output_csv,
            ["trade_date", "symbol", "sector_id", "sector_name", "mapping_source", "mapping_version"],
            rows,
        )

    def _fetch_symbol_history(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        try:
            frame = self.ak.stock_industry_change_cninfo(
                symbol=symbol,
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
            )
        except Exception:
            return []
        history: list[dict[str, Any]] = []
        for row in frame.to_dict(orient="records"):
            change_date = date.fromisoformat(str(row["变更日期"]))
            sector_name = self._pick_sector_name(row)
            history.append(
                {
                    "change_date": change_date,
                    "sector_name": sector_name,
                    "sector_id": self._normalize_sector_id(sector_name),
                }
            )
        history.sort(key=lambda item: item["change_date"])
        return history

    def _expand_history(
        self,
        symbol: str,
        trade_dates: list[date],
        history: list[dict[str, Any]],
    ) -> list[SectorMappingRecord]:
        rows: list[SectorMappingRecord] = []
        earliest_known = history[0] if history and self.config.backfill_earliest_known else None
        for trade_date in trade_dates:
            if earliest_known is not None:
                sector_name = str(earliest_known["sector_name"])
                sector_id = str(earliest_known["sector_id"])
            else:
                sector_name = self.config.fallback_sector_name
                sector_id = self.config.fallback_sector_id

            for item in history:
                if item["change_date"] <= trade_date:
                    sector_name = str(item["sector_name"])
                    sector_id = str(item["sector_id"])
                else:
                    break

            rows.append(
                SectorMappingRecord(
                    trade_date=trade_date,
                    symbol=symbol,
                    sector_id=sector_id,
                    sector_name=sector_name,
                    mapping_source=self.config.mapping_source,
                    mapping_version=self.config.mapping_version,
                )
            )
        return rows

    def _pick_sector_name(self, row: dict[str, Any]) -> str:
        preferred = str(row.get(self.config.classification_field, "")).strip()
        if preferred and preferred.lower() != "nan":
            return preferred
        for key in ("行业中类", "行业大类", "行业次类", "行业门类"):
            value = str(row.get(key, "")).strip()
            if value and value.lower() != "nan":
                return value
        return self.config.fallback_sector_name

    def _normalize_sector_id(self, sector_name: str) -> str:
        return (
            sector_name.upper()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("-", "_")
        )
