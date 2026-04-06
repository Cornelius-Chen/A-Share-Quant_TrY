from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v115n_cpo_intraday_strict_band_held_position_overlay_replay_v1 import (
    _costs,
    _load_daily_bars,
    _max_drawdown,
)
from a_share_quant.strategy.v120c_cpo_catalyst_event_registry_bootstrap_v1 import load_json_report


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_trade_date(value: str) -> datetime.date:
    return datetime.strptime(value, "%Y-%m-%d").date()


@dataclass(slots=True)
class V124BCpoHeatAwareAddLadderAuditReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V124BCpoHeatAwareAddLadderAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _next_trade_date(self, trade_date: str, trade_dates: list[datetime.date]) -> str | None:
        current = parse_trade_date(trade_date)
        for candidate in trade_dates:
            if candidate > current:
                return candidate.strftime("%Y-%m-%d")
        return None

    def analyze(self) -> tuple[V124BCpoHeatAwareAddLadderAuditReport, list[dict[str, Any]]]:
        v113t_payload = load_json_report(self.repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json")
        v114t_payload = load_json_report(self.repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json")
        v120e_payload = load_json_report(self.repo_root / "reports" / "analysis" / "v120e_cpo_research_test_baseline_overlay_replay_v1.json")
        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)

        baseline_orders_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in list(v114t_payload.get("executed_order_rows", [])):
            baseline_orders_by_exec.setdefault(str(row["execution_trade_date"]), []).append(row)
        trade_dates = [parse_trade_date(str(row["trade_date"])) for row in list(v114t_payload.get("replay_day_rows", []))]

        overlay_orders_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in list(v120e_payload.get("aggregated_signal_rows", [])):
            execution_trade_date = self._next_trade_date(str(row["signal_trade_date"]), trade_dates)
            if execution_trade_date is None:
                continue
            overlay_orders_by_exec.setdefault(execution_trade_date, []).append(row)

        variant_defs = [
            {
                "variant_name": "balanced_heat_reference",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
                "ladder": {1: 0.25, 2: 0.35, 3: 0.50, 4: 0.50},
            },
            {
                "variant_name": "balanced_ladder_mid_20_30_40",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
                "ladder": {1: 0.20, 2: 0.30, 3: 0.40, 4: 0.40},
            },
            {
                "variant_name": "balanced_ladder_soft_15_25_35",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
                "ladder": {1: 0.15, 2: 0.25, 3: 0.35, 4: 0.35},
            },
            {
                "variant_name": "balanced_ladder_flat_20_25_30",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
                "ladder": {1: 0.20, 2: 0.25, 3: 0.30, 4: 0.30},
            },
            {
                "variant_name": "balanced_ladder_convex_10_25_45",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
                "ladder": {1: 0.10, 2: 0.25, 3: 0.45, 4: 0.45},
            },
        ]

        variant_rows: list[dict[str, Any]] = []
        daily_state_rows: list[dict[str, Any]] = []

        for variant in variant_defs:
            cash = 1_000_000.0
            positions: dict[str, int] = {}
            equity_curve: list[float] = []
            executed_add_count = 0
            executed_add_notional = 0.0

            for trade_date in trade_dates:
                trade_date_str = trade_date.strftime("%Y-%m-%d")

                for row in baseline_orders_by_exec.get(trade_date_str, []):
                    symbol = str(row["symbol"])
                    action = str(row["action"])
                    quantity = int(row["quantity"])
                    execution_price = _to_float(row["execution_price"])
                    notional = quantity * execution_price
                    if action == "buy":
                        cash -= notional + _to_float(row["total_cost"])
                        positions[symbol] = positions.get(symbol, 0) + quantity
                    else:
                        sell_qty = min(quantity, positions.get(symbol, 0))
                        proceeds = sell_qty * execution_price
                        cash += proceeds - _to_float(row["total_cost"])
                        positions[symbol] = max(0, positions.get(symbol, 0) - sell_qty)

                open_mark_to_market = cash
                open_symbol_values: dict[str, float] = {}
                for symbol, qty in positions.items():
                    if qty <= 0:
                        continue
                    bar = daily_bars.get((symbol, trade_date))
                    if bar is None:
                        continue
                    symbol_value = qty * _to_float(bar["open"])
                    open_symbol_values[symbol] = symbol_value
                    open_mark_to_market += symbol_value

                for row in overlay_orders_by_exec.get(trade_date_str, []):
                    symbol = str(row["symbol"])
                    held_qty = positions.get(symbol, 0)
                    if held_qty <= 0:
                        continue
                    if any(
                        str(base_row["symbol"]) == symbol and str(base_row["action"]) == "sell"
                        for base_row in baseline_orders_by_exec.get(trade_date_str, [])
                    ):
                        continue
                    bar = daily_bars.get((symbol, trade_date))
                    if bar is None:
                        continue
                    execution_price = _to_float(bar["open"])
                    if execution_price <= 0:
                        continue

                    vote_count = int(row["component_count"])
                    ladder_fraction = float(variant["ladder"].get(vote_count, variant["ladder"][4]))
                    held_value = held_qty * execution_price
                    raw_target_notional = held_value * ladder_fraction

                    equity_open = max(open_mark_to_market, 1.0)
                    symbol_value_open = open_symbol_values.get(symbol, 0.0)
                    symbol_cap_room = max(0.0, float(variant["symbol_cap_ratio"]) * equity_open - symbol_value_open)
                    gross_cap_room = max(0.0, float(variant["gross_cap_ratio"]) * equity_open - sum(open_symbol_values.values()))
                    cash_floor_room = max(0.0, cash - float(variant["cash_floor_ratio"]) * equity_open)
                    target_notional = min(raw_target_notional, 100000.0, cash, symbol_cap_room, gross_cap_room, cash_floor_room)

                    quantity = int((target_notional / execution_price) // 100) * 100
                    if quantity <= 0:
                        continue
                    notional = quantity * execution_price
                    costs = _costs(action="buy", notional=notional)
                    total_cash_need = notional + _to_float(costs["total_cost"])
                    if total_cash_need > cash:
                        continue
                    cash -= total_cash_need
                    positions[symbol] = positions.get(symbol, 0) + quantity
                    open_symbol_values[symbol] = open_symbol_values.get(symbol, 0.0) + notional
                    executed_add_count += 1
                    executed_add_notional += notional

                equity = cash
                gross_value = 0.0
                for symbol, qty in positions.items():
                    if qty <= 0:
                        continue
                    bar = daily_bars.get((symbol, trade_date))
                    if bar is None:
                        continue
                    gross_value += qty * _to_float(bar["close"])
                equity += gross_value
                equity_curve.append(equity)

                daily_state_rows.append(
                    {
                        "variant_name": variant["variant_name"],
                        "trade_date": trade_date_str,
                        "equity": round(equity, 4),
                        "cash": round(cash, 4),
                        "cash_ratio": round(cash / equity, 6) if equity > 0 else 0.0,
                        "gross_ratio": round(gross_value / equity, 6) if equity > 0 else 0.0,
                        "300308_qty": int(positions.get("300308", 0)),
                        "300502_qty": int(positions.get("300502", 0)),
                        "300757_qty": int(positions.get("300757", 0)),
                        "688498_qty": int(positions.get("688498", 0)),
                    }
                )

            variant_rows.append(
                {
                    "variant_name": variant["variant_name"],
                    "overlay_order_count": executed_add_count,
                    "overlay_notional_total": round(executed_add_notional, 4),
                    "final_equity": round(equity_curve[-1], 4) if equity_curve else 1_000_000.0,
                    "max_drawdown": round(_max_drawdown(equity_curve), 6) if equity_curve else 0.0,
                    "delta_vs_baseline": round((equity_curve[-1] if equity_curve else 1_000_000.0) - float(v114t_payload["summary"]["final_equity"]), 4),
                }
            )

        best_row = max(variant_rows, key=lambda row: row["final_equity"] - 2_500_000 * row["max_drawdown"])
        summary = {
            "acceptance_posture": "freeze_v124b_cpo_heat_aware_add_ladder_audit_v1",
            "baseline_final_equity": float(v114t_payload["summary"]["final_equity"]),
            "baseline_max_drawdown": 0.134272,
            "variant_count": len(variant_rows),
            "best_tradeoff_variant_name": str(best_row["variant_name"]),
            "recommended_next_posture": "compare_best_heat_ladder_to_top_drawdown_intervals_before_triage",
        }
        interpretation = [
            "V1.24B keeps heat as the only live execution control and only changes the add ladder under that heat budget.",
            "The purpose is to test whether the research line is still over-aggressive because of per-hit add size, not because heat control itself is wrong.",
        ]
        return V124BCpoHeatAwareAddLadderAuditReport(
            summary=summary,
            variant_rows=variant_rows,
            interpretation=interpretation,
        ), daily_state_rows


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124BCpoHeatAwareAddLadderAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_daily_state_csv(*, output_path: Path, rows: list[dict[str, Any]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124BCpoHeatAwareAddLadderAuditAnalyzer(repo_root=repo_root)
    result, daily_state_rows = analyzer.analyze()
    report_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124b_cpo_heat_aware_add_ladder_audit_v1",
        result=result,
    )
    csv_path = write_daily_state_csv(
        output_path=repo_root / "data" / "training" / "cpo_heat_aware_add_ladder_daily_state_v1.csv",
        rows=daily_state_rows,
    )
    print(report_path)
    print(csv_path)


if __name__ == "__main__":
    main()
