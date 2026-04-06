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
class V122XCpoBaselineDailyStateRebuildReport:
    summary: dict[str, Any]
    daily_state_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "daily_state_rows": self.daily_state_rows,
            "interpretation": self.interpretation,
        }


class V122XCpoBaselineDailyStateRebuildAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V122XCpoBaselineDailyStateRebuildReport:
        v114t_payload = json.loads(
            (self.repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")
        )
        replay_day_rows = list(v114t_payload.get("replay_day_rows", []))
        executed_order_rows = list(v114t_payload.get("executed_order_rows", []))
        daily_bar_rows = _load_csv_rows(
            self.repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
        )
        close_map = {
            (str(row["trade_date"]), str(row["symbol"])): _to_float(row.get("close"))
            for row in daily_bar_rows
        }
        symbols = ["300308", "300502", "300757", "688498"]

        orders_by_exec_date: dict[str, list[dict[str, Any]]] = {}
        for row in executed_order_rows:
            orders_by_exec_date.setdefault(str(row["execution_trade_date"]), []).append(row)

        positions = {symbol: 0 for symbol in symbols}
        daily_state_rows: list[dict[str, Any]] = []

        for replay_row in replay_day_rows:
            trade_date = str(replay_row["trade_date"])
            for order_row in orders_by_exec_date.get(trade_date, []):
                symbol = str(order_row["symbol"])
                if symbol not in positions:
                    continue
                quantity = int(_to_float(order_row["quantity"]))
                if str(order_row["action"]) == "buy":
                    positions[symbol] += quantity
                else:
                    positions[symbol] = max(0, positions[symbol] - quantity)

            held_symbols = [symbol for symbol in symbols if positions[symbol] > 0]
            market_value = 0.0
            for symbol in held_symbols:
                market_value += positions[symbol] * close_map.get((trade_date, symbol), 0.0)

            daily_state_rows.append(
                {
                    "trade_date": trade_date,
                    "equity": round(_to_float(replay_row["equity_after_close"]), 4),
                    "cash": round(_to_float(replay_row["cash_after_close"]), 4),
                    "held_symbols": ",".join(held_symbols) if held_symbols else "CASH",
                    "position_count": len(held_symbols),
                    "300308_qty": positions["300308"],
                    "300502_qty": positions["300502"],
                    "300757_qty": positions["300757"],
                    "688498_qty": positions["688498"],
                    "reconstructed_market_value": round(market_value, 4),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v122x_cpo_baseline_daily_state_rebuild_v1",
            "row_count": len(daily_state_rows),
            "first_trade_date": daily_state_rows[0]["trade_date"] if daily_state_rows else None,
            "last_trade_date": daily_state_rows[-1]["trade_date"] if daily_state_rows else None,
            "recommended_next_posture": "compare_baseline_and_research_test_drawdown_attribution_on_same_intervals",
        }
        interpretation = [
            "V1.22X rebuilds baseline daily state from the repaired replay so drawdown attribution can be compared interval-by-interval against the research test baseline.",
            "The goal is not to rerun baseline logic, but to make holdings, cash, and mark-to-market exposure directly comparable on the same dates.",
        ]
        return V122XCpoBaselineDailyStateRebuildReport(
            summary=summary,
            daily_state_rows=daily_state_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122XCpoBaselineDailyStateRebuildReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_daily_state_csv(*, output_path: Path, rows: list[dict[str, Any]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return output_path
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122XCpoBaselineDailyStateRebuildAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122x_cpo_baseline_daily_state_rebuild_v1",
        result=result,
    )
    write_daily_state_csv(
        output_path=repo_root / "data" / "training" / "cpo_baseline_daily_state_v1.csv",
        rows=result.daily_state_rows,
    )
    print(output_path)


if __name__ == "__main__":
    main()
