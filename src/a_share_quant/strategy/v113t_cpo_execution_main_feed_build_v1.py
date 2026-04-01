from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


@dataclass(slots=True)
class V113TCPOExecutionMainFeedBuildReport:
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


def load_security_master(path: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            symbol = str(row.get("symbol", "")).strip()
            if not symbol:
                continue
            result[symbol] = {
                "board": str(row.get("board", "")).strip(),
                "exchange": str(row.get("exchange", "")).strip(),
                "list_date": str(row.get("list_date", "")).strip(),
            }
    return result


def sina_symbol(symbol: str) -> str:
    if symbol.startswith(("600", "601", "603", "605", "688")):
        return f"sh{symbol}"
    return f"sz{symbol}"


def infer_board(symbol: str) -> str:
    if symbol.startswith("688"):
        return "STAR"
    if symbol.startswith(("300", "301")):
        return "ChiNext"
    return "Main"


def fetch_sina_daily_rows(symbol: str) -> list[dict[str, Any]]:
    response = requests.get(
        "https://quotes.sina.cn/cn/api/openapi.php/CN_MarketDataService.getKLineData",
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
        raise ValueError(f"Sina fetch failed for {symbol}: {status}")
    rows = list(result.get("data", []))
    if not rows:
        raise ValueError(f"No daily bars returned for {symbol}")
    return rows


class V113TCPOExecutionMainFeedBuildAnalyzer:
    def analyze(
        self,
        *,
        repo_root: Path,
        v112aa_payload: dict[str, Any],
    ) -> V113TCPOExecutionMainFeedBuildReport:
        cohort_rows = list(v112aa_payload.get("object_role_time_rows", []))
        if not cohort_rows:
            raise ValueError("V1.13T expects the CPO bounded cohort map.")

        security_master = load_security_master(
            repo_root / "data" / "reference" / "security_master" / "akshare_security_master_market_research_v1.csv"
        )
        output_path = repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
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
            "board",
            "exchange",
            "data_source",
            "quality_tier",
        ]

        csv_rows: list[dict[str, Any]] = []
        symbol_rows: list[dict[str, Any]] = []
        for row in cohort_rows:
            symbol = str(row["symbol"])
            fetched_rows = sorted(fetch_sina_daily_rows(symbol), key=lambda item: str(item["day"]))
            meta = security_master.get(symbol, {})
            list_date_raw = str(meta.get("list_date") or fetched_rows[0]["day"])
            list_date = datetime.strptime(list_date_raw, "%Y-%m-%d").date()
            prev_close: float | None = None
            for item in fetched_rows:
                trade_date = datetime.strptime(str(item["day"]), "%Y-%m-%d").date()
                close_price = float(item["close"])
                open_price = float(item["open"])
                high_price = float(item["high"])
                low_price = float(item["low"])
                volume = float(item["volume"])
                turnover = round(close_price * volume, 4)
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
                        "listed_days": (trade_date - list_date).days + 1,
                        "board": str(meta.get("board") or infer_board(symbol)),
                        "exchange": str(meta.get("exchange") or ("SSE" if symbol.startswith(("600", "601", "603", "605", "688")) else "SZSE")),
                        "data_source": "sina_openapi_execution_main_feed",
                        "quality_tier": "execution_main_feed_candidate",
                    }
                )
                prev_close = close_price

            symbol_rows.append(
                {
                    "symbol": symbol,
                    "cohort_layer": str(row["cohort_layer"]),
                    "role_family": str(row["role_family"]),
                    "row_count": len(fetched_rows),
                    "first_trade_date": str(fetched_rows[0]["day"]),
                    "last_trade_date": str(fetched_rows[-1]["day"]),
                    "board": str(meta.get("board") or infer_board(symbol)),
                    "exchange": str(meta.get("exchange") or ("SSE" if symbol.startswith(("600", "601", "603", "605", "688")) else "SZSE")),
                }
            )

        csv_rows = sorted(csv_rows, key=lambda item: (str(item["trade_date"]), str(item["symbol"])))
        with output_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)

        summary = {
            "acceptance_posture": "freeze_v113t_cpo_execution_main_feed_build_v1",
            "board_name": "CPO",
            "cohort_symbol_count": len(cohort_rows),
            "execution_main_feed_symbol_count": len(symbol_rows),
            "execution_main_feed_row_count": len(csv_rows),
            "output_csv": str(output_path.relative_to(repo_root)),
            "recommended_next_posture": "audit_execution_main_feed_completeness_and_then_bind_it_into_full_board_cpo_replay",
        }
        interpretation = [
            "V1.13T builds a single CPO-wide daily execution main feed candidate with uniform columns and symbol coverage.",
            "Unlike the training proxy framing in V1.13R, this feed is intended to become the execution-layer primary price table for paper replay and stricter simulation.",
            "This still needs a completeness audit before claiming full-board replay readiness.",
        ]
        return V113TCPOExecutionMainFeedBuildReport(
            summary=summary,
            symbol_rows=symbol_rows,
            interpretation=interpretation,
        )


def write_v113t_cpo_execution_main_feed_build_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113TCPOExecutionMainFeedBuildReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
