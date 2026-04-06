from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from a_share_quant.data.tushare_client import build_tushare_pro


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _normalize_compact_date(raw: str) -> str:
    raw = (raw or "").strip()
    if len(raw) == 8 and raw.isdigit():
        return f"{raw[0:4]}-{raw[4:6]}-{raw[6:8]}"
    return raw


def _target_start() -> date:
    return date(2024, 1, 1)


def _target_end() -> date:
    return date(2027, 12, 31)


@dataclass(slots=True)
class MaterializedAShareTradeCalendarBootstrapV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareTradeCalendarBootstrapV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "market_registry"
            / "a_share_trade_calendar_registry_v1.csv"
        )

    @staticmethod
    def _coverage_ok(rows: list[dict[str, str]]) -> bool:
        if not rows:
            return False
        coverage_start = min(row["cal_date"] for row in rows)
        coverage_end = max(row["cal_date"] for row in rows)
        return coverage_start <= _target_start().isoformat() and coverage_end >= _target_end().isoformat()

    @staticmethod
    def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def _fetch_rows(self) -> list[dict[str, Any]]:
        pro = build_tushare_pro(repo_root=self.repo_root)
        frame = pro.trade_cal(
            exchange="SSE",
            start_date=_target_start().strftime("%Y%m%d"),
            end_date=_target_end().strftime("%Y%m%d"),
        )
        rows: list[dict[str, Any]] = []
        for record in frame.to_dict("records"):
            rows.append(
                {
                    "exchange": str(record.get("exchange", "SSE") or "SSE"),
                    "cal_date": _normalize_compact_date(str(record.get("cal_date", ""))),
                    "is_open": str(record.get("is_open", "")),
                    "pretrade_date": _normalize_compact_date(str(record.get("pretrade_date", ""))),
                }
            )
        rows.sort(key=lambda row: row["cal_date"])
        if not rows:
            raise RuntimeError("Tushare trade_cal returned no rows.")
        return rows

    def materialize(self) -> MaterializedAShareTradeCalendarBootstrapV1:
        rows = _read_csv(self.output_path)
        if not self._coverage_ok(rows):
            rows = self._fetch_rows()
            self._write_csv(self.output_path, rows)

        open_day_count = sum(1 for row in rows if row["is_open"] == "1")
        now_cn = datetime.now(ZoneInfo("Asia/Shanghai")).date().isoformat()
        today_row = next((row for row in rows if row["cal_date"] == now_cn), None)
        summary = {
            "calendar_row_count": len(rows),
            "open_day_count": open_day_count,
            "coverage_start": rows[0]["cal_date"],
            "coverage_end": rows[-1]["cal_date"],
            "today_calendar_state": (
                "trading_day" if today_row and today_row["is_open"] == "1" else "non_trading_day"
            ),
            "authoritative_output": "a_share_trade_calendar_registry_materialized",
        }
        return MaterializedAShareTradeCalendarBootstrapV1(summary=summary, rows=rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareTradeCalendarBootstrapV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
