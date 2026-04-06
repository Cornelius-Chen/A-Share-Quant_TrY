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
from a_share_quant.strategy.v120e_cpo_research_test_baseline_overlay_replay_v1 import (
    CpoResearchTestBaselineOverlayReplayAnalyzer,
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_trade_date(value: str) -> datetime.date:
    return datetime.strptime(value, "%Y-%m-%d").date()


@dataclass(slots=True)
class V122ZCpoResearchTestBaselineHeatGuardrailReviewReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V122ZCpoResearchTestBaselineHeatGuardrailReviewAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _next_trade_date(self, trade_date: str, trade_dates: list[datetime.date]) -> str | None:
        current = parse_trade_date(trade_date)
        for candidate in trade_dates:
            if candidate > current:
                return candidate.strftime("%Y-%m-%d")
        return None

    def analyze(self) -> V122ZCpoResearchTestBaselineHeatGuardrailReviewReport:
        v113t_payload = load_json_report(self.repo_root / "reports/analysis/v113t_cpo_execution_main_feed_build_v1.json")
        v114t_payload = load_json_report(self.repo_root / "reports/analysis/v114t_cpo_replay_integrity_repair_v1.json")
        v120e_payload = load_json_report(self.repo_root / "reports/analysis/v120e_cpo_research_test_baseline_overlay_replay_v1.json")
        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)

        baseline_orders = list(v114t_payload.get("executed_order_rows", []))
        trade_dates = [parse_trade_date(str(row["trade_date"])) for row in list(v114t_payload.get("replay_day_rows", []))]
        baseline_orders_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in baseline_orders:
            baseline_orders_by_exec.setdefault(str(row["execution_trade_date"]), []).append(row)

        aggregated_signal_rows = list(v120e_payload.get("aggregated_signal_rows", []))
        overlay_orders_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in aggregated_signal_rows:
            execution_trade_date = self._next_trade_date(str(row["signal_trade_date"]), trade_dates)
            if execution_trade_date is None:
                continue
            overlay_orders_by_exec.setdefault(execution_trade_date, []).append(row)

        variant_defs = [
            {
                "variant_name": "uncapped_reference",
                "symbol_cap_ratio": 9.99,
                "gross_cap_ratio": 9.99,
                "cash_floor_ratio": 0.0,
            },
            {
                "variant_name": "mild_heat_guardrail",
                "symbol_cap_ratio": 0.35,
                "gross_cap_ratio": 0.80,
                "cash_floor_ratio": 0.20,
            },
            {
                "variant_name": "balanced_heat_guardrail",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
            },
            {
                "variant_name": "strict_heat_guardrail",
                "symbol_cap_ratio": 0.25,
                "gross_cap_ratio": 0.60,
                "cash_floor_ratio": 0.35,
            },
        ]

        variant_rows: list[dict[str, Any]] = []

        for variant in variant_defs:
            cash = 1_000_000.0
            positions: dict[str, int] = {}
            equity_curve: list[float] = []
            executed_overlay_rows: list[dict[str, Any]] = []

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
                current_gross_ratio = 0.0 if open_mark_to_market <= 0 else sum(open_symbol_values.values()) / open_mark_to_market

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
                    symbol_cap_room = max(0.0, variant["symbol_cap_ratio"] * equity_open - symbol_value_open)
                    gross_cap_room = max(0.0, variant["gross_cap_ratio"] * equity_open - sum(open_symbol_values.values()))
                    cash_floor_room = max(0.0, cash - variant["cash_floor_ratio"] * equity_open)
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
                    open_mark_to_market -= costs["total_cost"]
                    executed_overlay_rows.append(
                        {
                            "execution_trade_date": trade_date_str,
                            "symbol": symbol,
                            "component_count": vote_count,
                            "quantity": quantity,
                            "notional": round(notional, 4),
                        }
                    )

                equity = cash
                gross_value = 0.0
                for symbol, qty in positions.items():
                    if qty <= 0:
                        continue
                    bar = daily_bars.get((symbol, trade_date))
                    if bar is None:
                        continue
                    symbol_value = qty * _to_float(bar["close"])
                    gross_value += symbol_value
                    equity += symbol_value
                max_cash_ratio = cash / equity if equity > 0 else 0.0
                gross_ratio = gross_value / equity if equity > 0 else 0.0
                equity_curve.append(equity)

            variant_rows.append(
                {
                    "variant_name": variant["variant_name"],
                    "symbol_cap_ratio": variant["symbol_cap_ratio"],
                    "gross_cap_ratio": variant["gross_cap_ratio"],
                    "cash_floor_ratio": variant["cash_floor_ratio"],
                    "overlay_order_count": len(executed_overlay_rows),
                    "final_equity": round(equity_curve[-1], 4) if equity_curve else 1_000_000.0,
                    "max_drawdown": round(_max_drawdown(equity_curve), 6) if equity_curve else 0.0,
                    "delta_vs_baseline": round((equity_curve[-1] if equity_curve else 1_000_000.0) - float(v114t_payload["summary"]["final_equity"]), 4),
                }
            )

        best_row = max(variant_rows, key=lambda row: row["final_equity"] - 2_500_000 * row["max_drawdown"])
        summary = {
            "acceptance_posture": "freeze_v122z_cpo_research_test_baseline_heat_guardrail_review_v1",
            "baseline_final_equity": float(v114t_payload["summary"]["final_equity"]),
            "baseline_max_drawdown": 0.134272,
            "variant_count": len(variant_rows),
            "best_tradeoff_variant_name": best_row["variant_name"],
            "recommended_next_posture": "use_heat_guardrail_review_to_decide_if_position_heat_is_the_first_fix_before_reduce_logic",
        }
        interpretation = [
            "V1.22Z compares simple heat guardrails on the research test baseline rather than introducing new factors.",
            "The purpose is to see whether the main failure mode is excessive carry and low cash, or whether a real reduce-side rule is still the only viable fix.",
        ]
        return V122ZCpoResearchTestBaselineHeatGuardrailReviewReport(
            summary=summary,
            variant_rows=variant_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V122ZCpoResearchTestBaselineHeatGuardrailReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V122ZCpoResearchTestBaselineHeatGuardrailReviewAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v122z_cpo_research_test_baseline_heat_guardrail_review_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
