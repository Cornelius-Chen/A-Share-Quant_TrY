from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


@dataclass(slots=True)
class V113RCPOFullBoardDailyBarProxyCompletionReport:
    summary: dict[str, Any]
    symbol_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_rows": self.symbol_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def sina_symbol(symbol: str) -> str:
    if symbol.startswith(("600", "601", "603", "605", "688")):
        return f"sh{symbol}"
    return f"sz{symbol}"


def fetch_sina_daily_rows(symbol: str) -> list[dict[str, Any]]:
    url = "https://quotes.sina.cn/cn/api/openapi.php/CN_MarketDataService.getKLineData"
    response = requests.get(
        url,
        params={
            "symbol": sina_symbol(symbol),
            "scale": "240",
            "ma": "no",
            "datalen": "1023",
        },
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    result = payload.get("result", {})
    status = result.get("status", {})
    if int(status.get("code", -1)) != 0:
        raise ValueError(f"Sina daily fetch failed for {symbol}: {status}")
    rows = list(result.get("data", []))
    if not rows:
        raise ValueError(f"Sina daily fetch returned no rows for {symbol}.")
    return rows


class V113RCPOFullBoardDailyBarProxyCompletionAnalyzer:
    def analyze(
        self,
        *,
        repo_root: Path,
        v112aa_payload: dict[str, Any],
    ) -> V113RCPOFullBoardDailyBarProxyCompletionReport:
        cohort_rows = list(v112aa_payload.get("object_role_time_rows", []))
        if not cohort_rows:
            raise ValueError("V1.13R expects the CPO bounded cohort map.")

        output_path = repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_full_board_proxy_v1.csv"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
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
            "data_source",
            "quality_tier",
        ]

        symbol_rows: list[dict[str, Any]] = []
        csv_rows: list[dict[str, Any]] = []
        for row in cohort_rows:
            symbol = str(row["symbol"])
            fetched = fetch_sina_daily_rows(symbol)
            fetched = sorted(fetched, key=lambda item: str(item["day"]))
            prev_close: float | None = None
            first_trade_date: datetime | None = None
            for item in fetched:
                trade_date = datetime.strptime(str(item["day"]), "%Y-%m-%d").date()
                if first_trade_date is None:
                    first_trade_date = datetime.combine(trade_date, datetime.min.time())
                close_price = float(item["close"])
                open_price = float(item["open"])
                high_price = float(item["high"])
                low_price = float(item["low"])
                volume = float(item["volume"])
                turnover = round(close_price * volume, 4)
                listed_days = (trade_date - first_trade_date.date()).days + 1
                csv_rows.append(
                    {
                        "trade_date": str(trade_date),
                        "symbol": symbol,
                        "open": round(open_price, 4),
                        "high": round(high_price, 4),
                        "low": round(low_price, 4),
                        "close": round(close_price, 4),
                        "volume": round(volume, 4),
                        "turnover": turnover,
                        "pre_close": round(prev_close if prev_close is not None else close_price, 4),
                        "adjust_factor": 1.0,
                        "is_st": False,
                        "is_suspended": False,
                        "listed_days": listed_days,
                        "data_source": "sina_openapi_proxy",
                        "quality_tier": "proxy_for_training_only",
                    }
                )
                prev_close = close_price

            symbol_rows.append(
                {
                    "symbol": symbol,
                    "cohort_layer": str(row["cohort_layer"]),
                    "role_family": str(row["role_family"]),
                    "row_count": len(fetched),
                    "first_trade_date": str(fetched[0]["day"]),
                    "last_trade_date": str(fetched[-1]["day"]),
                    "data_source": "sina_openapi_proxy",
                    "quality_tier": "proxy_for_training_only",
                }
            )

        csv_rows = sorted(csv_rows, key=lambda item: (str(item["trade_date"]), str(item["symbol"])))
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

        summary = {
            "acceptance_posture": "freeze_v113r_cpo_full_board_daily_bar_proxy_completion_v1",
            "board_name": "CPO",
            "cohort_symbol_count": len(cohort_rows),
            "proxy_completed_symbol_count": len(symbol_rows),
            "proxy_daily_bar_row_count": len(csv_rows),
            "output_csv": str(output_path.relative_to(repo_root)),
            "training_use_allowed": True,
            "execution_use_allowed": False,
            "recommended_next_posture": "use_proxy_daily_bars_for_board_level_training_only_and_keep_execution_on_stricter_market_feed",
        }
        interpretation = [
            "V1.13R supplements the missing CPO daily-bar coverage with a proxy public feed so board-level training no longer depends on the narrow two-symbol local market-research subset.",
            "The proxy feed is explicitly marked training-only. It should not silently replace the stricter execution feed.",
            "This completion solves board-wide daily price coverage for training, but not high-quality execution-grade market-state completeness.",
        ]
        return V113RCPOFullBoardDailyBarProxyCompletionReport(
            summary=summary,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_v113r_cpo_full_board_daily_bar_proxy_completion_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113RCPOFullBoardDailyBarProxyCompletionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
