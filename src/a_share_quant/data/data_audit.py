from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _safe_float(value: str) -> float | None:
    text = str(value).strip()
    if text == "":
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


@dataclass(slots=True)
class DataAuditConfig:
    protocol_version: str
    output_path: Path
    tables: dict[str, Path]

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "DataAuditConfig":
        return cls(
            protocol_version=str(config.get("protocol_version", "protocol_v1.0")),
            output_path=Path(config["paths"]["output_path"]),
            tables={
                str(name): Path(path)
                for name, path in config["tables"].items()
            },
        )


class DataPackAuditor:
    """Audit the current canonical and derived tables for completeness and basic quality."""

    REQUIRED_FIELDS: dict[str, list[str]] = {
        "daily_bars": [
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
        "index_daily_bars": [
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
        "security_master": [
            "symbol",
            "name",
            "list_date",
            "delist_date",
            "board",
            "exchange",
        ],
        "trading_calendar": [
            "trade_date",
            "is_open",
            "prev_open_date",
            "next_open_date",
        ],
        "adjustment_factors": [
            "trade_date",
            "symbol",
            "adjust_factor",
        ],
        "sector_mapping_daily": [
            "trade_date",
            "symbol",
            "sector_id",
            "sector_name",
            "mapping_source",
            "mapping_version",
        ],
        "concept_mapping_daily": [
            "trade_date",
            "symbol",
            "concept_id",
            "concept_name",
            "mapping_source",
            "mapping_version",
            "is_primary_concept",
            "weight",
        ],
        "sector_snapshots": [
            "trade_date",
            "sector_id",
            "sector_name",
            "persistence",
            "diffusion",
            "money_making",
            "leader_strength",
            "relative_strength",
            "activity",
        ],
        "stock_snapshots": [
            "trade_date",
            "symbol",
            "sector_id",
            "sector_name",
            "expected_upside",
            "drive_strength",
            "stability",
            "liquidity",
            "late_mover_quality",
            "resonance",
        ],
        "mainline_windows": [
            "window_id",
            "symbol",
            "start_date",
            "end_date",
            "capturable_return",
        ],
    }

    PRIMARY_KEYS: dict[str, list[str]] = {
        "daily_bars": ["trade_date", "symbol"],
        "index_daily_bars": ["trade_date", "symbol"],
        "security_master": ["symbol"],
        "trading_calendar": ["trade_date"],
        "adjustment_factors": ["trade_date", "symbol"],
        "sector_mapping_daily": ["trade_date", "symbol", "sector_id"],
        "concept_mapping_daily": ["trade_date", "symbol", "concept_id"],
        "sector_snapshots": ["trade_date", "sector_id"],
        "stock_snapshots": ["trade_date", "symbol"],
        "mainline_windows": ["window_id"],
    }

    CANONICAL_TABLES = (
        "daily_bars",
        "index_daily_bars",
        "security_master",
        "trading_calendar",
        "adjustment_factors",
        "sector_mapping_daily",
    )

    DERIVED_TABLES = (
        "sector_snapshots",
        "stock_snapshots",
        "mainline_windows",
    )

    def __init__(self, config: DataAuditConfig) -> None:
        self.config = config

    def build_report(self) -> dict[str, Any]:
        table_reports = {
            name: self._audit_table(name, path)
            for name, path in self.config.tables.items()
        }
        canonical_ready = sum(
            1
            for name in self.CANONICAL_TABLES
            if table_reports.get(name, {}).get("status") == "ready"
        )
        canonical_partial = sum(
            1
            for name in self.CANONICAL_TABLES
            if table_reports.get(name, {}).get("status") == "bootstrap_partial"
        )
        canonical_missing = sum(
            1
            for name in self.CANONICAL_TABLES
            if table_reports.get(name, {}).get("status") == "missing"
        )
        derived_ready = sum(
            1
            for name in self.DERIVED_TABLES
            if table_reports.get(name, {}).get("status") in {"ready", "bootstrap_partial"}
        )
        warnings = sum(
            len(report.get("warnings", []))
            for report in table_reports.values()
        )
        errors = sum(
            len(report.get("errors", []))
            for report in table_reports.values()
        )
        report = {
            "protocol_version": self.config.protocol_version,
            "summary": {
                "canonical_ready_count": canonical_ready,
                "canonical_partial_count": canonical_partial,
                "canonical_missing_count": canonical_missing,
                "derived_ready_count": derived_ready,
                "table_warning_count": warnings,
                "table_error_count": errors,
                "baseline_ready": canonical_missing == 0 and canonical_partial == 0,
            },
            "tables": table_reports,
        }
        return report

    def write_report(self, report: dict[str, Any]) -> Path:
        self.config.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.config.output_path.open("w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)
        return self.config.output_path

    def _audit_table(self, name: str, path: Path) -> dict[str, Any]:
        required_fields = self.REQUIRED_FIELDS.get(name, [])
        primary_key = self.PRIMARY_KEYS.get(name, [])

        if not path.exists():
            if name == "concept_mapping_daily":
                return {
                    "path": str(path),
                    "status": "optional_missing",
                    "row_count": 0,
                    "warnings": ["optional_table_missing"],
                    "errors": [],
                }
            return {
                "path": str(path),
                "status": "missing",
                "row_count": 0,
                "warnings": [],
                "errors": ["file_not_found"],
            }

        fieldnames, rows = _read_csv_rows(path)
        missing_fields = [field for field in required_fields if field not in fieldnames]
        duplicate_count = self._duplicate_key_count(rows, primary_key)
        warnings: list[str] = []
        errors: list[str] = []

        if missing_fields:
            errors.append(f"missing_required_fields:{','.join(missing_fields)}")
        if duplicate_count > 0:
            errors.append(f"duplicate_primary_keys:{duplicate_count}")

        coverage = self._coverage(rows)
        warnings.extend(self._table_specific_warnings(name, rows))
        errors.extend(self._table_specific_errors(name, rows))

        status = "ready"
        if errors:
            if any(item.startswith("missing_required_fields:") for item in errors):
                status = "bootstrap_partial"
            else:
                status = "error"
        elif warnings:
            status = "bootstrap_partial"

        return {
            "path": str(path),
            "status": status,
            "row_count": len(rows),
            "columns": fieldnames,
            "missing_required_fields": missing_fields,
            "duplicate_primary_key_count": duplicate_count,
            "coverage": coverage,
            "warnings": warnings,
            "errors": errors,
        }

    def _duplicate_key_count(self, rows: list[dict[str, str]], primary_key: list[str]) -> int:
        if not primary_key:
            return 0
        seen: set[tuple[str, ...]] = set()
        duplicates = 0
        for row in rows:
            key = tuple(str(row.get(field, "")) for field in primary_key)
            if key in seen:
                duplicates += 1
            else:
                seen.add(key)
        return duplicates

    def _coverage(self, rows: list[dict[str, str]]) -> dict[str, Any]:
        if not rows:
            return {}
        date_values = [
            row["trade_date"]
            for row in rows
            if row.get("trade_date")
        ]
        symbol_values = [
            row["symbol"]
            for row in rows
            if row.get("symbol")
        ]
        coverage: dict[str, Any] = {}
        if date_values:
            coverage["date_min"] = min(date_values)
            coverage["date_max"] = max(date_values)
            coverage["unique_date_count"] = len(set(date_values))
        if symbol_values:
            coverage["unique_symbol_count"] = len(set(symbol_values))
        return coverage

    def _table_specific_warnings(self, name: str, rows: list[dict[str, str]]) -> list[str]:
        if not rows:
            return ["empty_table"]

        warnings: list[str] = []
        if name == "daily_bars":
            factors = {_safe_float(row.get("adjust_factor", "")) for row in rows}
            if factors == {1.0}:
                warnings.append("adjust_factor_all_one")
            if all(str(row.get("listed_days", "0")).strip() in {"", "0"} for row in rows):
                warnings.append("listed_days_all_zero")
        elif name == "security_master":
            if "list_date" not in rows[0]:
                warnings.append("missing_list_date")
            if "delist_date" not in rows[0]:
                warnings.append("missing_delist_date")
        elif name == "adjustment_factors":
            if all(_safe_float(row.get("adjust_factor", "")) in {None, 1.0} for row in rows):
                warnings.append("adjust_factor_values_not_informative")
        elif name == "sector_mapping_daily":
            versions = {str(row.get("mapping_version", "")).strip() for row in rows}
            if len(versions) == 1 and "bootstrap" in next(iter(versions), ""):
                warnings.append("bootstrap_mapping_version")
        elif name == "concept_mapping_daily":
            versions = {str(row.get("mapping_version", "")).strip() for row in rows}
            if len(versions) == 1 and "bootstrap" in next(iter(versions), ""):
                warnings.append("bootstrap_concept_mapping_version")
        elif name in {"sector_snapshots", "stock_snapshots", "mainline_windows"}:
            warnings.append("derived_bootstrap_table")
        return warnings

    def _table_specific_errors(self, name: str, rows: list[dict[str, str]]) -> list[str]:
        errors: list[str] = []
        if name in {"daily_bars", "index_daily_bars"}:
            invalid = 0
            for row in rows:
                open_price = _safe_float(row.get("open", ""))
                high_price = _safe_float(row.get("high", ""))
                low_price = _safe_float(row.get("low", ""))
                close_price = _safe_float(row.get("close", ""))
                volume = _safe_float(row.get("volume", ""))
                turnover = _safe_float(row.get("turnover", ""))
                pre_close = _safe_float(row.get("pre_close", ""))
                if None in {open_price, high_price, low_price, close_price, volume, turnover, pre_close}:
                    invalid += 1
                    continue
                if high_price < low_price:
                    invalid += 1
                if min(open_price, high_price, low_price, close_price, pre_close) <= 0:
                    invalid += 1
                if volume < 0 or turnover < 0:
                    invalid += 1
            if invalid:
                errors.append(f"invalid_price_or_volume_rows:{invalid}")
        elif name == "trading_calendar":
            invalid = sum(1 for row in rows if not row.get("trade_date"))
            if invalid:
                errors.append(f"missing_trade_date_rows:{invalid}")
        elif name == "sector_mapping_daily":
            invalid = sum(
                1
                for row in rows
                if not row.get("sector_id") or not row.get("mapping_source")
            )
            if invalid:
                errors.append(f"incomplete_mapping_rows:{invalid}")
        elif name == "concept_mapping_daily":
            invalid = sum(
                1
                for row in rows
                if not row.get("concept_id") or not row.get("mapping_source")
            )
            if invalid:
                errors.append(f"incomplete_concept_mapping_rows:{invalid}")
        return errors
