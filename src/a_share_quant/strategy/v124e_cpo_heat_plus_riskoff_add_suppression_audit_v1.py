from __future__ import annotations

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


def _quantile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    idx = max(0, min(len(ordered) - 1, int(round((len(ordered) - 1) * q))))
    return ordered[idx]


@dataclass(slots=True)
class V124ECpoHeatPlusRiskoffAddSuppressionAuditReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V124ECpoHeatPlusRiskoffAddSuppressionAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _next_trade_date(self, trade_date: str, trade_dates: list[datetime.date]) -> str | None:
        current = parse_trade_date(trade_date)
        for candidate in trade_dates:
            if candidate > current:
                return candidate.strftime("%Y-%m-%d")
        return None

    def _load_overlay_orders_by_exec(self, *, trade_dates: list[datetime.date]) -> dict[str, list[dict[str, Any]]]:
        payload = load_json_report(
            self.repo_root / "reports" / "analysis" / "v120e_cpo_research_test_baseline_overlay_replay_v1.json"
        )
        overlay_orders_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in list(payload.get("aggregated_signal_rows", [])):
            execution_trade_date = self._next_trade_date(str(row["signal_trade_date"]), trade_dates)
            if execution_trade_date is None:
                continue
            overlay_orders_by_exec.setdefault(execution_trade_date, []).append(row)
        return overlay_orders_by_exec

    def _load_riskoff_signals(
        self,
        *,
        trade_dates: list[datetime.date],
    ) -> tuple[dict[str, list[dict[str, Any]]], dict[str, float]]:
        payload = load_json_report(
            self.repo_root / "reports" / "analysis" / "v121j_cpo_reduce_side_board_risk_off_external_audit_v1.json"
        )
        scored_rows = list(payload.get("scored_rows", []))
        score_values = [_to_float(row["board_risk_off_reduce_score_candidate"]) for row in scored_rows]
        thresholds = {
            "q75": round(_quantile(score_values, 0.75), 6),
            "q85": round(_quantile(score_values, 0.85), 6),
            "q90": round(_quantile(score_values, 0.90), 6),
        }
        signals_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in scored_rows:
            execution_trade_date = self._next_trade_date(str(row["signal_trade_date"]), trade_dates)
            if execution_trade_date is None:
                continue
            signals_by_exec.setdefault(execution_trade_date, []).append(
                {
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "score": _to_float(row["board_risk_off_reduce_score_candidate"]),
                }
            )
        return signals_by_exec, thresholds

    def analyze(self) -> V124ECpoHeatPlusRiskoffAddSuppressionAuditReport:
        v113t_payload = load_json_report(self.repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json")
        v114t_payload = load_json_report(self.repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json")
        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)

        trade_dates = [parse_trade_date(str(row["trade_date"])) for row in list(v114t_payload.get("replay_day_rows", []))]
        baseline_orders_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in list(v114t_payload.get("executed_order_rows", [])):
            baseline_orders_by_exec.setdefault(str(row["execution_trade_date"]), []).append(row)

        overlay_orders_by_exec = self._load_overlay_orders_by_exec(trade_dates=trade_dates)
        riskoff_signals_by_exec, riskoff_thresholds = self._load_riskoff_signals(trade_dates=trade_dates)

        variant_defs = [
            {
                "variant_name": "balanced_heat_reference",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
                "riskoff_quantile": None,
                "heat_gross_trigger": None,
                "heat_symbol_trigger": None,
            },
            {
                "variant_name": "balanced_add_suppress_q75_g55_s20",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
                "riskoff_quantile": "q75",
                "heat_gross_trigger": 0.55,
                "heat_symbol_trigger": 0.20,
            },
            {
                "variant_name": "balanced_add_suppress_q85_g55_s20",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
                "riskoff_quantile": "q85",
                "heat_gross_trigger": 0.55,
                "heat_symbol_trigger": 0.20,
            },
            {
                "variant_name": "balanced_add_suppress_q85_g60_s20",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
                "riskoff_quantile": "q85",
                "heat_gross_trigger": 0.60,
                "heat_symbol_trigger": 0.20,
            },
            {
                "variant_name": "balanced_add_suppress_q85_g55_s25",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
                "riskoff_quantile": "q85",
                "heat_gross_trigger": 0.55,
                "heat_symbol_trigger": 0.25,
            },
            {
                "variant_name": "balanced_add_suppress_q90_g55_s20",
                "symbol_cap_ratio": 0.30,
                "gross_cap_ratio": 0.70,
                "cash_floor_ratio": 0.25,
                "riskoff_quantile": "q90",
                "heat_gross_trigger": 0.55,
                "heat_symbol_trigger": 0.20,
            },
        ]

        variant_rows: list[dict[str, Any]] = []

        for variant in variant_defs:
            cash = 1_000_000.0
            positions: dict[str, int] = {}
            equity_curve: list[float] = []
            executed_add_count = 0
            suppressed_add_count = 0

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

                riskoff_threshold = None
                riskoff_rows_for_day = []
                if variant["riskoff_quantile"] is not None:
                    riskoff_threshold = riskoff_thresholds[str(variant["riskoff_quantile"])]
                    riskoff_rows_for_day = riskoff_signals_by_exec.get(trade_date_str, [])

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

                    equity_open = max(open_mark_to_market, 1.0)
                    symbol_value_open = open_symbol_values.get(symbol, 0.0)
                    gross_ratio_open = sum(open_symbol_values.values()) / equity_open
                    symbol_ratio_open = symbol_value_open / equity_open

                    if riskoff_threshold is not None:
                        matching = next((r for r in riskoff_rows_for_day if str(r["symbol"]) == symbol), None)
                        if matching is not None:
                            if (
                                _to_float(matching["score"]) >= riskoff_threshold
                                and gross_ratio_open >= float(variant["heat_gross_trigger"])
                                and symbol_ratio_open >= float(variant["heat_symbol_trigger"])
                            ):
                                suppressed_add_count += 1
                                continue

                    vote_count = int(row["component_count"])
                    target_fraction = 0.25
                    if vote_count == 2:
                        target_fraction = 0.35
                    elif vote_count >= 3:
                        target_fraction = 0.50
                    held_value = held_qty * execution_price
                    raw_target_notional = held_value * target_fraction

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

                equity = cash
                for symbol, qty in positions.items():
                    if qty <= 0:
                        continue
                    bar = daily_bars.get((symbol, trade_date))
                    if bar is None:
                        continue
                    equity += qty * _to_float(bar["close"])
                equity_curve.append(equity)

            final_equity = equity_curve[-1] if equity_curve else 1_000_000.0
            variant_rows.append(
                {
                    "variant_name": variant["variant_name"],
                    "riskoff_quantile": variant["riskoff_quantile"] or "none",
                    "heat_gross_trigger": variant["heat_gross_trigger"] if variant["heat_gross_trigger"] is not None else "none",
                    "heat_symbol_trigger": variant["heat_symbol_trigger"] if variant["heat_symbol_trigger"] is not None else "none",
                    "executed_add_count": executed_add_count,
                    "suppressed_add_count": suppressed_add_count,
                    "final_equity": round(final_equity, 4),
                    "max_drawdown": round(_max_drawdown(equity_curve), 6) if equity_curve else 0.0,
                    "delta_vs_baseline": round(final_equity - float(v114t_payload["summary"]["final_equity"]), 4),
                }
            )

        def objective(row: dict[str, Any]) -> float:
            return _to_float(row["final_equity"]) - 2_500_000 * _to_float(row["max_drawdown"])

        best_tradeoff = max(variant_rows, key=objective)
        summary = {
            "acceptance_posture": "freeze_v124e_cpo_heat_plus_riskoff_add_suppression_audit_v1",
            "baseline_final_equity": float(v114t_payload["summary"]["final_equity"]),
            "baseline_max_drawdown": 0.134272,
            "variant_count": len(variant_rows),
            "riskoff_thresholds": riskoff_thresholds,
            "best_tradeoff_variant_name": str(best_tradeoff["variant_name"]),
            "recommended_next_posture": "triage_add_suppression_vs_plain_heat_before_any_more_downside_execution_work",
        }
        interpretation = [
            "V1.24E keeps heat as the live control and tests a milder downside grammar: stop adding when broad risk-off appears inside already-hot states.",
            "This is intentionally less aggressive than selling, because the previous execution attempts showed that broad de-risk destroyed too much return.",
        ]
        return V124ECpoHeatPlusRiskoffAddSuppressionAuditReport(
            summary=summary,
            variant_rows=variant_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V124ECpoHeatPlusRiskoffAddSuppressionAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V124ECpoHeatPlusRiskoffAddSuppressionAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v124e_cpo_heat_plus_riskoff_add_suppression_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
