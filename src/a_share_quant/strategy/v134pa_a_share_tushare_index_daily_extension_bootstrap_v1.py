from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.data.tushare_client import build_tushare_pro


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _ts_code_from_symbol(symbol: str) -> str:
    if symbol.startswith("399"):
        return f"{symbol}.SZ"
    return f"{symbol}.SH"


def _compact_to_iso(compact: str) -> str:
    return f"{compact[:4]}-{compact[4:6]}-{compact[6:]}"


@dataclass(slots=True)
class V134PAAShareTushareIndexDailyExtensionBootstrapV1Report:
    summary: dict[str, Any]
    output_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "output_rows": self.output_rows,
            "interpretation": self.interpretation,
        }


class V134PAAShareTushareIndexDailyExtensionBootstrapV1Runner:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.index_registry_path = (
            repo_root / "data" / "reference" / "info_center" / "market_registry" / "a_share_index_market_registry_v1.csv"
        )
        self.output_path = repo_root / "data" / "raw" / "index_daily_bars" / "tushare_index_daily_bars_extension_v1.csv"
        self.start_date = date(2023, 9, 1)
        self.end_date = date(2026, 4, 3)
        self.pause_seconds = 0.15
        self.pro = build_tushare_pro(repo_root=repo_root)

    def run(self) -> V134PAAShareTushareIndexDailyExtensionBootstrapV1Report:
        registry_rows = _read_csv(self.index_registry_path)
        symbols = sorted({row["symbol"] for row in registry_rows})
        rows: list[dict[str, Any]] = []
        for symbol in symbols:
            ts_code = _ts_code_from_symbol(symbol)
            frame = self.pro.index_daily(
                ts_code=ts_code,
                start_date=self.start_date.strftime("%Y%m%d"),
                end_date=self.end_date.strftime("%Y%m%d"),
            )
            if frame is None or frame.empty:
                time.sleep(self.pause_seconds)
                continue
            for record in frame.to_dict(orient="records"):
                rows.append(
                    {
                        "trade_date": _compact_to_iso(str(record.get("trade_date", ""))),
                        "symbol": symbol,
                        "open": record.get("open"),
                        "high": record.get("high"),
                        "low": record.get("low"),
                        "close": record.get("close"),
                        "volume": record.get("vol"),
                        "turnover": record.get("amount"),
                        "pre_close": record.get("pre_close"),
                    }
                )
            time.sleep(self.pause_seconds)

        rows.sort(key=lambda row: (row["symbol"], row["trade_date"]))
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with self.output_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        per_symbol_counts: dict[str, int] = {}
        for row in rows:
            per_symbol_counts[row["symbol"]] = per_symbol_counts.get(row["symbol"], 0) + 1

        summary = {
            "provider": "tushare",
            "symbol_count": len(symbols),
            "row_count": len(rows),
            "coverage_start": min(row["trade_date"] for row in rows),
            "coverage_end": max(row["trade_date"] for row in rows),
            "artifact_path": str(self.output_path.relative_to(self.repo_root)),
            "authoritative_output": "a_share_tushare_index_daily_extension_raw_materialized",
        }
        output_rows = [
            {"symbol": symbol, "row_count": count, "ts_code": _ts_code_from_symbol(symbol)}
            for symbol, count in sorted(per_symbol_counts.items())
        ]
        interpretation = [
            "Tushare now materializes an index-daily raw extension beyond the legacy 2024 horizon.",
            "This closes the old no-source condition and converts replay-side movement from raw-source absence to post-intake re-audit work.",
        ]
        return V134PAAShareTushareIndexDailyExtensionBootstrapV1Report(summary, output_rows, interpretation)


def write_report(
    *, reports_dir: Path, report_name: str, result: V134PAAShareTushareIndexDailyExtensionBootstrapV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134PAAShareTushareIndexDailyExtensionBootstrapV1Runner(repo_root).run()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134pa_a_share_tushare_index_daily_extension_bootstrap_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
