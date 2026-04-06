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


def parse_trade_date(value: str) -> datetime.date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class CpoResearchTestBaselineOverlayReplayReport:
    summary: dict[str, Any]
    aggregated_signal_rows: list[dict[str, Any]]
    executed_overlay_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "aggregated_signal_rows": self.aggregated_signal_rows,
            "executed_overlay_rows": self.executed_overlay_rows,
            "interpretation": self.interpretation,
        }


class CpoResearchTestBaselineOverlayReplayAnalyzer:
    """Run a research-only overlay replay using all retained non-dead branches."""

    def _next_trade_date(self, trade_date: str, trade_dates: list[datetime.date]) -> str | None:
        current = parse_trade_date(trade_date)
        for candidate in trade_dates:
            if candidate > current:
                return candidate.strftime("%Y-%m-%d")
        return None

    def _load_candidate_hits(self) -> list[dict[str, Any]]:
        cooling = load_json_report(Path("reports/analysis/v117w_cpo_cooling_reacceleration_false_positive_control_discovery_v1.json"))
        cooling_ext = load_json_report(Path("reports/analysis/v117x_cpo_cooling_reacceleration_false_positive_control_external_audit_v1.json"))
        sustained = load_json_report(Path("reports/analysis/v118u_cpo_sustained_participation_non_chase_external_audit_v1.json"))
        elg = load_json_report(Path("reports/analysis/v119l_cpo_participation_turnover_elg_support_discovery_v1.json"))
        elg_ext = load_json_report(Path("reports/analysis/v119m_cpo_participation_turnover_elg_support_external_audit_v1.json"))
        cooled = load_json_report(Path("reports/analysis/v116z_cpo_quality_side_cooled_refinement_v1.json"))
        cooled_retention = load_json_report(Path("reports/analysis/v117a_cpo_quality_side_cooled_retention_v1.json"))

        rows: list[dict[str, Any]] = []

        cooling_threshold = float(cooling_ext["summary"]["best_threshold"])
        for row in list(cooling.get("control_rows", [])):
            if float(row.get("controlled_score", 0.0)) >= cooling_threshold:
                rows.append(
                    {
                        "signal_trade_date": str(row["signal_trade_date"]),
                        "symbol": str(row["symbol"]),
                        "component_name": "cooling_reacceleration_branch",
                        "score_field": "controlled_score",
                        "score_value": float(row["controlled_score"]),
                    }
                )

        sustained_threshold = float(sustained["summary"]["best_threshold"])
        for row in list(sustained.get("scored_rows", [])):
            if float(row.get("sustained_participation_non_chase_score", 0.0)) >= sustained_threshold:
                rows.append(
                    {
                        "signal_trade_date": str(row["signal_trade_date"]),
                        "symbol": str(row["symbol"]),
                        "component_name": "sustained_participation_non_chase",
                        "score_field": "sustained_participation_non_chase_score",
                        "score_value": float(row["sustained_participation_non_chase_score"]),
                    }
                )

        elg_threshold = float(elg_ext["summary"]["best_threshold"])
        for row in list(elg.get("candidate_score_rows", [])):
            if float(row.get("participation_turnover_elg_support_score", 0.0)) >= elg_threshold:
                rows.append(
                    {
                        "signal_trade_date": str(row["signal_trade_date"]),
                        "symbol": str(row["symbol"]),
                        "component_name": "participation_turnover_elg_support",
                        "score_field": "participation_turnover_elg_support_score",
                        "score_value": float(row["participation_turnover_elg_support_score"]),
                    }
                )

        retained_variant = str(cooled_retention["summary"]["retained_variant_name"])
        for row in list(cooled.get("hit_rows", [])):
            if str(row.get("variant_name")) == retained_variant:
                rows.append(
                    {
                        "signal_trade_date": str(row["signal_trade_date"]),
                        "symbol": str(row["symbol"]),
                        "component_name": retained_variant,
                        "score_field": "abs_visible_pc1_score_1030",
                        "score_value": abs(float(row.get("visible_pc1_score_1030", 0.0))),
                    }
                )

        return rows

    def analyze(self) -> CpoResearchTestBaselineOverlayReplayReport:
        v113t_payload = load_json_report(Path("reports/analysis/v113t_cpo_execution_main_feed_build_v1.json"))
        v114t_payload = load_json_report(Path("reports/analysis/v114t_cpo_replay_integrity_repair_v1.json"))
        daily_path = Path(str(v113t_payload["summary"]["output_csv"]))
        daily_bars = _load_daily_bars(daily_path)

        baseline_orders = list(v114t_payload.get("executed_order_rows", []))
        trade_dates = [parse_trade_date(str(row["trade_date"])) for row in list(v114t_payload.get("replay_day_rows", []))]
        baseline_orders_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in baseline_orders:
            baseline_orders_by_exec.setdefault(str(row["execution_trade_date"]), []).append(row)

        candidate_rows = self._load_candidate_hits()
        aggregated_map: dict[tuple[str, str], dict[str, Any]] = {}
        for row in candidate_rows:
            key = (row["signal_trade_date"], row["symbol"])
            bucket = aggregated_map.setdefault(
                key,
                {
                    "signal_trade_date": row["signal_trade_date"],
                    "symbol": row["symbol"],
                    "component_names": [],
                    "component_count": 0,
                    "max_score_value": 0.0,
                },
            )
            bucket["component_names"].append(str(row["component_name"]))
            bucket["component_count"] += 1
            bucket["max_score_value"] = max(bucket["max_score_value"], float(row["score_value"]))
        aggregated_signal_rows = sorted(
            aggregated_map.values(),
            key=lambda row: (row["signal_trade_date"], row["symbol"]),
        )

        overlay_orders_by_exec: dict[str, list[dict[str, Any]]] = {}
        for row in aggregated_signal_rows:
            execution_trade_date = self._next_trade_date(str(row["signal_trade_date"]), trade_dates)
            if execution_trade_date is None:
                continue
            overlay_orders_by_exec.setdefault(execution_trade_date, []).append(row)

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
                target_notional = min(held_value * target_fraction, 100000.0, cash)
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
                executed_overlay_rows.append(
                    {
                        "signal_trade_date": str(row["signal_trade_date"]),
                        "execution_trade_date": trade_date_str,
                        "symbol": symbol,
                        "action": "buy",
                        "component_names": "|".join(sorted(row["component_names"])),
                        "component_count": vote_count,
                        "quantity": quantity,
                        "execution_price": execution_price,
                        "notional": notional,
                        "commission": round(_to_float(costs["commission"]), 4),
                        "stamp_tax": round(_to_float(costs["stamp_tax"]), 4),
                        "slippage": round(_to_float(costs["slippage"]), 4),
                        "total_cost": round(_to_float(costs["total_cost"]), 4),
                        "weight_vs_initial_capital": round(notional / 1000000.0, 6),
                        "overlay_scope": "research_test_baseline_held_position_only_do_not_override_baseline_sell",
                        "execution_mode": "signal_on_t_close_execute_on_t_plus_1_open",
                    }
                )

            equity = cash
            for symbol, qty in positions.items():
                if qty <= 0:
                    continue
                bar = daily_bars.get((symbol, trade_date))
                if bar is None:
                    continue
                equity += qty * _to_float(bar["close"])
            equity_curve.append(equity)

        summary = {
            "acceptance_posture": "freeze_v120e_cpo_research_test_baseline_overlay_replay_v1",
            "execution_mode": "signal_on_t_close_execute_on_t_plus_1_open",
            "overlay_scope": "research_test_baseline_held_position_only_do_not_override_baseline_sell",
            "initial_capital": 1000000.0,
            "baseline_final_equity": float(v114t_payload["summary"]["final_equity"]),
            "baseline_max_drawdown": 0.134272,
            "research_overlay_order_count": len(executed_overlay_rows),
            "research_test_final_equity": round(equity_curve[-1], 4) if equity_curve else 1000000.0,
            "research_test_delta_vs_baseline": round((equity_curve[-1] if equity_curve else 1000000.0) - float(v114t_payload["summary"]["final_equity"]), 4),
            "research_test_max_drawdown": round(_max_drawdown(equity_curve), 6) if equity_curve else 0.0,
            "component_names_included": [
                "cooling_reacceleration_branch",
                "sustained_participation_non_chase",
                "participation_turnover_elg_support",
                "cooled_q_0p25",
            ],
            "excluded_non_dead_component_names": [
                "breakout_damage_soft_component",
            ],
            "recommended_next_posture": "treat_as_research_test_baseline_only_not_as_authoritative_system",
        }
        interpretation = [
            "This replay uses all retained non-dead branches inside one bounded research test baseline overlay.",
            "It is not authoritative because the retained branches still fail promotion gates and only support held-position overlay semantics.",
            "Breakout-damage remains excluded from execution because it is archived as a soft expectancy component without an honest row-level execution surface here.",
        ]
        return CpoResearchTestBaselineOverlayReplayReport(
            summary=summary,
            aggregated_signal_rows=aggregated_signal_rows,
            executed_overlay_rows=executed_overlay_rows,
            interpretation=interpretation,
        )


def write_cpo_research_test_baseline_overlay_replay_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CpoResearchTestBaselineOverlayReplayReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_cpo_research_test_baseline_overlay_csv(*, output_path: Path, rows: list[dict[str, Any]]) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        output_path.write_text("", encoding="utf-8")
        return output_path
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return output_path
