from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _load_csv_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V122WCpoResearchTestBaselineDrawdownAttributionReport:
    summary: dict[str, Any]
    drawdown_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "drawdown_rows": self.drawdown_rows,
            "interpretation": self.interpretation,
        }


class V122WCpoResearchTestBaselineDrawdownAttributionAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122WCpoResearchTestBaselineDrawdownAttributionReport:
        drawdown_payload = json.loads(
            (self.repo_root / "reports" / "analysis" / "v120k_cpo_research_test_baseline_top_drawdown_dashboard_v1.json").read_text(
                encoding="utf-8"
            )
        )
        daily_state_rows = _load_csv_rows(
            self.repo_root / "data" / "training" / "cpo_research_test_baseline_daily_state_v1.csv"
        )
        daily_state_map = {str(row["trade_date"]): row for row in daily_state_rows}
        trade_rows = _load_csv_rows(
            self.repo_root / "data" / "training" / "cpo_research_test_baseline_trade_explainer_v1.csv"
        )
        daily_bar_rows = _load_csv_rows(
            self.repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
        )
        close_map = {
            (str(row["trade_date"]), str(row["symbol"])): _to_float(row.get("close"))
            for row in daily_bar_rows
        }

        symbols = ["300308", "300502", "300757", "688498"]
        drawdown_rows: list[dict[str, Any]] = []

        for dd_row in drawdown_payload["top_drawdown_rows"]:
            peak_date = str(dd_row["peak_date"])
            trough_date = str(dd_row["trough_date"])
            peak_state = daily_state_map[peak_date]
            trough_state = daily_state_map[trough_date]

            peak_equity = _to_float(peak_state["equity"])
            peak_cash = _to_float(peak_state["cash"])
            trough_equity = _to_float(trough_state["equity"])
            trough_cash = _to_float(trough_state["cash"])

            symbol_contributions: list[dict[str, Any]] = []
            total_mark_to_market_change = 0.0
            for symbol in symbols:
                peak_qty = _to_float(peak_state.get(f"{symbol}_qty"))
                if peak_qty <= 0:
                    continue
                peak_close = close_map.get((peak_date, symbol), 0.0)
                trough_close = close_map.get((trough_date, symbol), 0.0)
                pnl_change = peak_qty * (trough_close - peak_close)
                total_mark_to_market_change += pnl_change
                symbol_contributions.append(
                    {
                        "symbol": symbol,
                        "peak_qty": int(peak_qty),
                        "peak_close": round(peak_close, 4),
                        "trough_close": round(trough_close, 4),
                        "mark_to_market_change": round(pnl_change, 4),
                    }
                )

            symbol_contributions.sort(key=lambda row: row["mark_to_market_change"])

            interval_trades = [
                row
                for row in trade_rows
                if peak_date <= str(row["execution_trade_date"]) <= trough_date
            ]
            interval_trade_rows = [
                {
                    "execution_trade_date": str(row["execution_trade_date"]),
                    "lane": str(row["lane"]),
                    "symbol": str(row["symbol"]),
                    "action": str(row["action"]),
                    "reason": str(row["reason"]),
                    "weight_vs_initial_capital": round(_to_float(row["weight_vs_initial_capital"]), 6),
                    "notional": round(_to_float(row["notional"]), 4),
                }
                for row in interval_trades
            ]

            drawdown_rows.append(
                {
                    "rank": dd_row["rank"],
                    "peak_date": peak_date,
                    "trough_date": trough_date,
                    "drawdown": dd_row["drawdown"],
                    "drawdown_amount": dd_row["drawdown_amount"],
                    "peak_equity": round(peak_equity, 4),
                    "trough_equity": round(trough_equity, 4),
                    "peak_cash": round(peak_cash, 4),
                    "trough_cash": round(trough_cash, 4),
                    "peak_cash_ratio": round(peak_cash / peak_equity if peak_equity else 0.0, 6),
                    "trough_cash_ratio": round(trough_cash / trough_equity if trough_equity else 0.0, 6),
                    "peak_held_symbols": str(peak_state["held_symbols"]),
                    "trough_held_symbols": str(trough_state["held_symbols"]),
                    "peak_position_count": int(_to_float(peak_state["position_count"])),
                    "trough_position_count": int(_to_float(trough_state["position_count"])),
                    "interval_trade_count": len(interval_trade_rows),
                    "interval_trade_rows": interval_trade_rows,
                    "symbol_contributions": symbol_contributions,
                    "estimated_mark_to_market_change_from_peak_positions": round(total_mark_to_market_change, 4),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v122w_cpo_research_test_baseline_drawdown_attribution_v1",
            "drawdown_count": len(drawdown_rows),
            "largest_drawdown_rank": drawdown_rows[0]["rank"] if drawdown_rows else None,
            "largest_drawdown_peak_date": drawdown_rows[0]["peak_date"] if drawdown_rows else None,
            "largest_drawdown_trough_date": drawdown_rows[0]["trough_date"] if drawdown_rows else None,
            "largest_drawdown_peak_cash_ratio": drawdown_rows[0]["peak_cash_ratio"] if drawdown_rows else None,
            "largest_drawdown_interval_trade_count": drawdown_rows[0]["interval_trade_count"] if drawdown_rows else None,
            "recommended_next_posture": "use_drawdown_attribution_to_decide_whether_next_work_should_focus_on_reduce_or_position_heat",
        }
        interpretation = [
            "V1.22W turns the top drawdown chart into attribution rather than just geometry.",
            "The purpose is to see whether the research test baseline mainly failed because it was too invested, too concentrated, or still adding at the wrong times.",
            "This is descriptive attribution only; it does not promote any candidate into execution.",
        ]
        return V122WCpoResearchTestBaselineDrawdownAttributionReport(
            summary=summary,
            drawdown_rows=drawdown_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122WCpoResearchTestBaselineDrawdownAttributionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122WCpoResearchTestBaselineDrawdownAttributionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122w_cpo_research_test_baseline_drawdown_attribution_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
