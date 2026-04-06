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
)
from a_share_quant.strategy.v120c_cpo_catalyst_event_registry_bootstrap_v1 import load_json_report


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_trade_date(value: str) -> datetime.date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _positions_string(positions: dict[str, int]) -> str:
    active = sorted(symbol for symbol, qty in positions.items() if qty > 0)
    return ",".join(active)


@dataclass(slots=True)
class V123LCpoHeatGuardrailDrawdownIntervalCompareReport:
    summary: dict[str, Any]
    interval_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "interval_rows": self.interval_rows,
            "interpretation": self.interpretation,
        }


class V123LCpoHeatGuardrailDrawdownIntervalCompareAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _next_trade_date(self, trade_date: str, trade_dates: list[datetime.date]) -> str | None:
        current = parse_trade_date(trade_date)
        for candidate in trade_dates:
            if candidate > current:
                return candidate.strftime("%Y-%m-%d")
        return None

    def _replay_variant_daily_state(
        self,
        *,
        variant_name: str,
        symbol_cap_ratio: float,
        gross_cap_ratio: float,
        cash_floor_ratio: float,
        trade_dates: list[datetime.date],
        daily_bars: dict[tuple[str, datetime.date], dict[str, Any]],
        baseline_orders_by_exec: dict[str, list[dict[str, Any]]],
        overlay_orders_by_exec: dict[str, list[dict[str, Any]]],
    ) -> list[dict[str, Any]]:
        cash = 1_000_000.0
        positions: dict[str, int] = {}
        daily_state_rows: list[dict[str, Any]] = []

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
                target_fraction = 0.25
                if vote_count == 2:
                    target_fraction = 0.35
                elif vote_count >= 3:
                    target_fraction = 0.50
                held_value = held_qty * execution_price
                raw_target_notional = held_value * target_fraction

                equity_open = max(open_mark_to_market, 1.0)
                symbol_value_open = open_symbol_values.get(symbol, 0.0)
                symbol_cap_room = max(0.0, symbol_cap_ratio * equity_open - symbol_value_open)
                gross_cap_room = max(0.0, gross_cap_ratio * equity_open - sum(open_symbol_values.values()))
                cash_floor_room = max(0.0, cash - cash_floor_ratio * equity_open)
                target_notional = min(raw_target_notional, 100000.0, cash, symbol_cap_room, gross_cap_room, cash_floor_room)

                quantity = int((target_notional / execution_price) // 100) * 100
                if quantity <= 0:
                    continue
                notional = quantity * execution_price
                costs = _costs(action="buy", notional=notional)
                total_cash_need = notional + costs["total_cost"]
                if total_cash_need > cash:
                    continue
                cash -= total_cash_need
                positions[symbol] = positions.get(symbol, 0) + quantity
                open_symbol_values[symbol] = open_symbol_values.get(symbol, 0.0) + notional

            gross_value = 0.0
            symbol_qty_rows: list[dict[str, Any]] = []
            for symbol, qty in positions.items():
                if qty <= 0:
                    continue
                bar = daily_bars.get((symbol, trade_date))
                if bar is None:
                    continue
                symbol_value = qty * _to_float(bar["close"])
                gross_value += symbol_value
                symbol_qty_rows.append({"symbol": symbol, "qty": qty})
            equity = cash + gross_value
            daily_state_rows.append(
                {
                    "variant_name": variant_name,
                    "trade_date": trade_date_str,
                    "equity": round(equity, 4),
                    "cash": round(cash, 4),
                    "cash_ratio": round(cash / equity, 6) if equity > 0 else 0.0,
                    "gross_ratio": round(gross_value / equity, 6) if equity > 0 else 0.0,
                    "held_symbols": _positions_string(positions),
                    "symbol_qty_rows": symbol_qty_rows,
                }
            )
        return daily_state_rows

    def analyze(self) -> V123LCpoHeatGuardrailDrawdownIntervalCompareReport:
        v113t_payload = load_json_report(self.repo_root / "reports/analysis/v113t_cpo_execution_main_feed_build_v1.json")
        v114t_payload = load_json_report(self.repo_root / "reports/analysis/v114t_cpo_replay_integrity_repair_v1.json")
        v120e_payload = load_json_report(self.repo_root / "reports/analysis/v120e_cpo_research_test_baseline_overlay_replay_v1.json")
        v122y_payload = load_json_report(self.repo_root / "reports/analysis/v122y_cpo_baseline_vs_research_drawdown_compare_v1.json")

        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)
        trade_dates = [parse_trade_date(str(row["trade_date"])) for row in list(v114t_payload.get("replay_day_rows", []))]

        baseline_orders_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in list(v114t_payload.get("executed_order_rows", [])):
            baseline_orders_by_exec.setdefault(str(row["execution_trade_date"]), []).append(row)

        overlay_orders_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in list(v120e_payload.get("aggregated_signal_rows", [])):
            execution_trade_date = self._next_trade_date(str(row["signal_trade_date"]), trade_dates)
            if execution_trade_date is None:
                continue
            overlay_orders_by_exec.setdefault(execution_trade_date, []).append(row)

        variant_defs = [
            ("uncapped_reference", 9.99, 9.99, 0.0),
            ("balanced_heat_guardrail", 0.30, 0.70, 0.25),
            ("strict_heat_guardrail", 0.25, 0.60, 0.35),
        ]
        state_map: dict[str, dict[str, dict[str, Any]]] = {}
        for variant_name, symbol_cap_ratio, gross_cap_ratio, cash_floor_ratio in variant_defs:
            rows = self._replay_variant_daily_state(
                variant_name=variant_name,
                symbol_cap_ratio=symbol_cap_ratio,
                gross_cap_ratio=gross_cap_ratio,
                cash_floor_ratio=cash_floor_ratio,
                trade_dates=trade_dates,
                daily_bars=daily_bars,
                baseline_orders_by_exec=baseline_orders_by_exec,
                overlay_orders_by_exec=overlay_orders_by_exec,
            )
            state_map[variant_name] = {row["trade_date"]: row for row in rows}

        interval_rows: list[dict[str, Any]] = []
        for interval in v122y_payload["interval_rows"]:
            peak_date = str(interval["peak_date"])
            trough_date = str(interval["trough_date"])
            uncapped_peak = state_map["uncapped_reference"][peak_date]
            uncapped_trough = state_map["uncapped_reference"][trough_date]
            row: dict[str, Any] = {
                "rank": int(interval["rank"]),
                "peak_date": peak_date,
                "trough_date": trough_date,
                "uncapped_drawdown": round((uncapped_peak["equity"] - uncapped_trough["equity"]) / uncapped_peak["equity"], 6),
                "uncapped_peak_equity": uncapped_peak["equity"],
                "uncapped_trough_equity": uncapped_trough["equity"],
                "uncapped_peak_cash_ratio": uncapped_peak["cash_ratio"],
                "uncapped_trough_cash_ratio": uncapped_trough["cash_ratio"],
                "uncapped_peak_symbols": uncapped_peak["held_symbols"],
                "uncapped_trough_symbols": uncapped_trough["held_symbols"],
            }

            uncapped_peak_qty = {item["symbol"]: int(item["qty"]) for item in uncapped_peak["symbol_qty_rows"]}
            uncapped_trough_qty = {item["symbol"]: int(item["qty"]) for item in uncapped_trough["symbol_qty_rows"]}

            for variant_name in ["balanced_heat_guardrail", "strict_heat_guardrail"]:
                peak_state = state_map[variant_name][peak_date]
                trough_state = state_map[variant_name][trough_date]
                peak_drawdown = (peak_state["equity"] - trough_state["equity"]) / peak_state["equity"] if peak_state["equity"] > 0 else 0.0
                peak_qty = {item["symbol"]: int(item["qty"]) for item in peak_state["symbol_qty_rows"]}
                trough_qty = {item["symbol"]: int(item["qty"]) for item in trough_state["symbol_qty_rows"]}
                qty_diffs = []
                for symbol in sorted(set(uncapped_peak_qty) | set(peak_qty) | set(uncapped_trough_qty) | set(trough_qty)):
                    qty_diffs.append(
                        {
                            "symbol": symbol,
                            "peak_qty_reduction_vs_uncapped": int(uncapped_peak_qty.get(symbol, 0) - peak_qty.get(symbol, 0)),
                            "trough_qty_reduction_vs_uncapped": int(uncapped_trough_qty.get(symbol, 0) - trough_qty.get(symbol, 0)),
                        }
                    )
                row[f"{variant_name}_drawdown"] = round(peak_drawdown, 6)
                row[f"{variant_name}_drawdown_improvement"] = round(row["uncapped_drawdown"] - peak_drawdown, 6)
                row[f"{variant_name}_peak_cash_ratio"] = peak_state["cash_ratio"]
                row[f"{variant_name}_trough_cash_ratio"] = trough_state["cash_ratio"]
                row[f"{variant_name}_peak_symbols"] = peak_state["held_symbols"]
                row[f"{variant_name}_trough_symbols"] = trough_state["held_symbols"]
                row[f"{variant_name}_qty_diffs_vs_uncapped"] = qty_diffs
            interval_rows.append(row)

        summary = {
            "acceptance_posture": "freeze_v123l_cpo_heat_guardrail_drawdown_interval_compare_v1",
            "interval_count": len(interval_rows),
            "variants_compared": ["uncapped_reference", "balanced_heat_guardrail", "strict_heat_guardrail"],
            "recommended_next_posture": "decide_if_heat_guardrail_should_be_prioritized_before_new_risk_side_factor_work",
        }
        interpretation = [
            "V1.23L compares the three main research-baseline heat variants on the same three drawdown windows already identified on the uncapped line.",
            "The goal is to answer a concrete question: how much of the pain is removed simply by carrying less, before any new reduce or close factor is added?",
        ]
        return V123LCpoHeatGuardrailDrawdownIntervalCompareReport(
            summary=summary,
            interval_rows=interval_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V123LCpoHeatGuardrailDrawdownIntervalCompareReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V123LCpoHeatGuardrailDrawdownIntervalCompareAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v123l_cpo_heat_guardrail_drawdown_interval_compare_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()

