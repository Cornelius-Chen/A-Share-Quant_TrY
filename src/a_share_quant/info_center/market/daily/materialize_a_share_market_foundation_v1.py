from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MaterializedAShareMarketFoundationV1:
    summary: dict[str, Any]
    daily_rows: list[dict[str, Any]]
    index_rows: list[dict[str, Any]]
    intraday_rows: list[dict[str, Any]]
    backlog_rows: list[dict[str, Any]]


class MaterializeAShareMarketFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.identity_path = (
            repo_root / "data" / "reference" / "info_center" / "identity" / "a_share_security_master_v1.csv"
        )
        self.daily_bars_path = repo_root / "data" / "raw" / "daily_bars" / "akshare_daily_bars_bootstrap.csv"
        self.index_daily_bars_path = (
            repo_root / "data" / "raw" / "index_daily_bars" / "akshare_index_daily_bars_bootstrap.csv"
        )
        self.intraday_root = repo_root / "data" / "raw" / "intraday_a_share_1min_monthly"
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "market_registry"
        self.daily_registry_path = self.output_dir / "a_share_daily_market_registry_v1.csv"
        self.index_registry_path = self.output_dir / "a_share_index_market_registry_v1.csv"
        self.intraday_registry_path = self.output_dir / "a_share_intraday_coverage_registry_v1.csv"
        self.backlog_path = self.output_dir / "a_share_board_state_backlog_v1.csv"
        self.manifest_path = self.output_dir / "a_share_market_foundation_manifest_v1.json"

    @staticmethod
    def _read_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def _group_summary(rows: list[dict[str, str]], *, symbol_key: str = "symbol") -> list[dict[str, Any]]:
        grouped: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            grouped.setdefault(row[symbol_key], []).append(row)
        output: list[dict[str, Any]] = []
        for symbol, symbol_rows in sorted(grouped.items()):
            ordered = sorted(symbol_rows, key=lambda row: row["trade_date"])
            output.append(
                {
                    "symbol": symbol,
                    "first_trade_date": ordered[0]["trade_date"],
                    "last_trade_date": ordered[-1]["trade_date"],
                    "row_count": len(ordered),
                    "suspended_row_count": sum(str(row.get("is_suspended", "")).lower() == "true" for row in ordered),
                    "st_row_count": sum(str(row.get("is_st", "")).lower() == "true" for row in ordered),
                    "latest_close": ordered[-1]["close"],
                }
            )
        return output

    def materialize(self) -> MaterializedAShareMarketFoundationV1:
        identity_rows = self._read_csv(self.identity_path)
        daily_rows = self._read_csv(self.daily_bars_path)
        index_rows = self._read_csv(self.index_daily_bars_path)

        identity_symbols = {row["symbol"] for row in identity_rows}
        daily_registry_rows = self._group_summary(daily_rows)
        for row in daily_registry_rows:
            row["identity_overlap"] = row["symbol"] in identity_symbols

        index_registry_rows = self._group_summary(index_rows)
        for row in index_registry_rows:
            row["identity_overlap"] = row["symbol"] in identity_symbols

        zip_paths = sorted(self.intraday_root.rglob("*_1min.zip"))
        intraday_rows: list[dict[str, Any]] = []
        for path in zip_paths:
            trade_date = path.stem.replace("_1min", "")
            intraday_rows.append(
                {
                    "trade_date": trade_date,
                    "storage_month": path.parent.name,
                    "coverage_status": "present_raw_zip",
                    "artifact_relpath": str(path.relative_to(self.repo_root)),
                }
            )

        backlog_rows = [
            {
                "market_component": "board_state_surface",
                "backlog_reason": "requires later derivation beyond raw daily and intraday coverage registries",
            },
            {
                "market_component": "limit_halt_surface",
                "backlog_reason": "requires dedicated limit-up limit-down and halt materialization",
            },
            {
                "market_component": "intraday_symbol_materialization",
                "backlog_reason": "raw zip coverage exists but full symbol-level minute expansion is deferred by storage policy",
            },
            {
                "market_component": "breadth_state_surface",
                "backlog_reason": "requires board breadth derivation after taxonomy and market registry bootstrap",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.daily_registry_path, daily_registry_rows)
        _write(self.index_registry_path, index_registry_rows)
        _write(self.intraday_registry_path, intraday_rows)
        _write(self.backlog_path, backlog_rows)

        summary = {
            "identity_symbol_count": len(identity_symbols),
            "daily_symbol_count": len(daily_registry_rows),
            "daily_identity_overlap_count": sum(row["identity_overlap"] for row in daily_registry_rows),
            "index_symbol_count": len(index_registry_rows),
            "intraday_trade_date_count": len(intraday_rows),
            "intraday_first_trade_date": intraday_rows[0]["trade_date"] if intraday_rows else "",
            "intraday_last_trade_date": intraday_rows[-1]["trade_date"] if intraday_rows else "",
            "board_state_backlog_count": len(backlog_rows),
            "daily_registry_path": str(self.daily_registry_path.relative_to(self.repo_root)),
            "index_registry_path": str(self.index_registry_path.relative_to(self.repo_root)),
            "intraday_registry_path": str(self.intraday_registry_path.relative_to(self.repo_root)),
            "backlog_path": str(self.backlog_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareMarketFoundationV1(
            summary=summary,
            daily_rows=daily_registry_rows,
            index_rows=index_registry_rows,
            intraday_rows=intraday_rows,
            backlog_rows=backlog_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareMarketFoundationV1(repo_root).materialize()
    print(result.summary["daily_registry_path"])


if __name__ == "__main__":
    main()
