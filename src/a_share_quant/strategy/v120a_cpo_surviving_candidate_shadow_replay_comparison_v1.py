from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v115p_cpo_intraday_timing_aware_overlay_replay_v1 import (
    V115PCpoIntradayTimingAwareOverlayReplayAnalyzer,
    _costs,
    _load_daily_bars,
    _max_drawdown,
    parse_trade_date,
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _lot_round(quantity: float) -> int:
    if quantity <= 0:
        return 0
    return int(quantity // 100) * 100


@dataclass(slots=True)
class V120ACpoSurvivingCandidateShadowReplayComparisonReport:
    summary: dict[str, Any]
    candidate_summary_rows: list[dict[str, Any]]
    overlay_order_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_summary_rows": self.candidate_summary_rows,
            "overlay_order_rows": self.overlay_order_rows,
            "interpretation": self.interpretation,
        }


class V120ACpoSurvivingCandidateShadowReplayComparisonAnalyzer:
    INITIAL_CAPITAL = 1_000_000.0
    FILL_FRACTION = 0.5
    PER_SYMBOL_ADD_CAP_RATIO = 0.5
    MAX_EXTRA_NOTIONAL_PER_SIGNAL = 100_000.0

    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _build_next_trade_date_map(trade_dates: list[date]) -> dict[date, date]:
        return {
            trade_dates[idx]: trade_dates[idx + 1]
            for idx in range(len(trade_dates) - 1)
        }

    @staticmethod
    def _baseline_orders_by_exec_date(executed_orders: list[dict[str, Any]]) -> dict[date, list[dict[str, Any]]]:
        result: dict[date, list[dict[str, Any]]] = {}
        for row in executed_orders:
            exec_date = parse_trade_date(str(row["execution_trade_date"]))
            result.setdefault(exec_date, []).append(row)
        return result

    @staticmethod
    def _next_day_sell_symbols(
        *,
        executed_orders: list[dict[str, Any]],
    ) -> set[tuple[date, str]]:
        blocked: set[tuple[date, str]] = set()
        for row in executed_orders:
            if str(row.get("action")) != "sell":
                continue
            blocked.add((parse_trade_date(str(row["execution_trade_date"])), str(row["symbol"])))
        return blocked

    @staticmethod
    def _cooling_rows(v117w_payload: dict[str, Any], v117x_payload: dict[str, Any]) -> list[dict[str, Any]]:
        threshold = _to_float(v117x_payload["summary"]["best_threshold"])
        rows: list[dict[str, Any]] = []
        for row in list(v117w_payload.get("control_rows", [])):
            score = _to_float(row.get("controlled_score"))
            if score < threshold:
                continue
            rows.append(
                {
                    "candidate_name": "cooling_reacceleration_controlled",
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "signal_score": score,
                    "signal_score_field": "controlled_score",
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                }
            )
        return rows

    @staticmethod
    def _sustained_rows(v118u_payload: dict[str, Any]) -> list[dict[str, Any]]:
        threshold = _to_float(v118u_payload["summary"]["best_threshold"])
        rows: list[dict[str, Any]] = []
        for row in list(v118u_payload.get("scored_rows", [])):
            score = _to_float(row.get("sustained_participation_non_chase_score"))
            if score < threshold:
                continue
            rows.append(
                {
                    "candidate_name": "sustained_participation_non_chase",
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "signal_score": score,
                    "signal_score_field": "sustained_participation_non_chase_score",
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                }
            )
        return rows

    @staticmethod
    def _elg_rows(v119l_payload: dict[str, Any], v119m_payload: dict[str, Any]) -> list[dict[str, Any]]:
        threshold = _to_float(v119m_payload["summary"]["best_threshold"])
        rows: list[dict[str, Any]] = []
        for row in list(v119l_payload.get("candidate_score_rows", [])):
            score = _to_float(row.get("participation_turnover_elg_support_score"))
            if score < threshold:
                continue
            rows.append(
                {
                    "candidate_name": "participation_turnover_elg_support",
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "signal_score": score,
                    "signal_score_field": "participation_turnover_elg_support_score",
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                }
            )
        return rows

    @staticmethod
    def _cooled_rows(v116z_payload: dict[str, Any], v117a_payload: dict[str, Any]) -> list[dict[str, Any]]:
        retained_variant = str(v117a_payload["summary"]["retained_variant_name"])
        rows: list[dict[str, Any]] = []
        for row in list(v116z_payload.get("hit_rows", [])):
            if str(row.get("variant_name")) != retained_variant:
                continue
            rows.append(
                {
                    "candidate_name": "cooled_q_0p25",
                    "signal_trade_date": str(row["signal_trade_date"]),
                    "symbol": str(row["symbol"]),
                    "signal_score": abs(_to_float(row.get("visible_pc1_score_1030"))),
                    "signal_score_field": "abs_visible_pc1_score_1030",
                    "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                    "max_adverse_return_3d": _to_float(row.get("max_adverse_return_3d")),
                }
            )
        return rows

    @staticmethod
    def _dedupe_candidate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[tuple[str, str, str]] = set()
        deduped: list[dict[str, Any]] = []
        for row in sorted(rows, key=lambda item: (str(item["signal_trade_date"]), str(item["symbol"]))):
            key = (str(row["candidate_name"]), str(row["signal_trade_date"]), str(row["symbol"]))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(row)
        return deduped

    def _candidate_row_groups(
        self,
        *,
        v116z_payload: dict[str, Any],
        v117a_payload: dict[str, Any],
        v117w_payload: dict[str, Any],
        v117x_payload: dict[str, Any],
        v118u_payload: dict[str, Any],
        v119l_payload: dict[str, Any],
        v119m_payload: dict[str, Any],
    ) -> dict[str, list[dict[str, Any]]]:
        return {
            "cooling_reacceleration_controlled": self._dedupe_candidate_rows(
                self._cooling_rows(v117w_payload, v117x_payload)
            ),
            "sustained_participation_non_chase": self._dedupe_candidate_rows(self._sustained_rows(v118u_payload)),
            "participation_turnover_elg_support": self._dedupe_candidate_rows(
                self._elg_rows(v119l_payload, v119m_payload)
            ),
            "cooled_q_0p25": self._dedupe_candidate_rows(self._cooled_rows(v116z_payload, v117a_payload)),
        }

    def _filter_to_overlay_candidates(
        self,
        *,
        candidate_rows: list[dict[str, Any]],
        baseline_positions_eod: dict[tuple[date, str], int],
        next_trade_date_map: dict[date, date],
        baseline_next_day_sell_symbols: set[tuple[date, str]],
        daily_bars: dict[tuple[str, date], dict[str, Any]],
    ) -> list[dict[str, Any]]:
        filtered: list[dict[str, Any]] = []
        for row in candidate_rows:
            signal_trade_date = parse_trade_date(str(row["signal_trade_date"]))
            next_trade_date = next_trade_date_map.get(signal_trade_date)
            symbol = str(row["symbol"])
            if next_trade_date is None:
                continue
            if baseline_positions_eod.get((signal_trade_date, symbol), 0) <= 0:
                continue
            if (next_trade_date, symbol) in baseline_next_day_sell_symbols:
                continue
            if (symbol, next_trade_date) not in daily_bars:
                continue
            filtered.append(row)
        return filtered

    def _build_overlay_orders(
        self,
        *,
        candidate_name: str,
        candidate_rows: list[dict[str, Any]],
        baseline_positions_eod: dict[tuple[date, str], int],
        next_trade_date_map: dict[date, date],
        daily_bars: dict[tuple[str, date], dict[str, Any]],
        starting_cash: float,
    ) -> list[dict[str, Any]]:
        cash = starting_cash
        orders: list[dict[str, Any]] = []
        for row in sorted(candidate_rows, key=lambda item: (str(item["signal_trade_date"]), str(item["symbol"]))):
            signal_trade_date = parse_trade_date(str(row["signal_trade_date"]))
            execution_trade_date = next_trade_date_map[signal_trade_date]
            symbol = str(row["symbol"])
            held_qty = baseline_positions_eod.get((signal_trade_date, symbol), 0)
            signal_bar = daily_bars.get((symbol, signal_trade_date))
            execution_bar = daily_bars.get((symbol, execution_trade_date))
            if signal_bar is None or execution_bar is None or held_qty <= 0:
                continue
            signal_close = _to_float(signal_bar["close"])
            execution_open = _to_float(execution_bar["open"])
            held_value = held_qty * signal_close
            target_notional = min(
                held_value * self.PER_SYMBOL_ADD_CAP_RATIO,
                self.MAX_EXTRA_NOTIONAL_PER_SIGNAL,
                cash * self.FILL_FRACTION,
            )
            quantity = _lot_round(target_notional / execution_open) if execution_open > 0 else 0
            if quantity <= 0:
                continue
            notional = quantity * execution_open
            costs = _costs(action="buy", notional=notional)
            total_cash_need = notional + costs["total_cost"]
            if total_cash_need > cash:
                quantity = _lot_round((cash / max(execution_open, 1e-9)) * 0.95)
                notional = quantity * execution_open
                costs = _costs(action="buy", notional=notional)
                total_cash_need = notional + costs["total_cost"]
            if quantity <= 0 or total_cash_need > cash:
                continue
            cash -= total_cash_need
            orders.append(
                {
                    "candidate_name": candidate_name,
                    "signal_trade_date": str(signal_trade_date),
                    "execution_trade_date": str(execution_trade_date),
                    "symbol": symbol,
                    "action": "buy",
                    "signal_score": round(_to_float(row["signal_score"]), 6),
                    "signal_score_field": str(row["signal_score_field"]),
                    "held_qty_on_signal_close": held_qty,
                    "held_close_price_on_signal_date": round(signal_close, 4),
                    "quantity": quantity,
                    "execution_price": round(execution_open, 4),
                    "notional": round(notional, 4),
                    "commission": costs["commission"],
                    "stamp_tax": costs["stamp_tax"],
                    "slippage": costs["slippage"],
                    "total_cost": costs["total_cost"],
                    "expectancy_proxy_3d": round(_to_float(row["expectancy_proxy_3d"]), 6),
                    "max_adverse_return_3d": round(_to_float(row["max_adverse_return_3d"]), 6),
                    "execution_mode": "signal_on_t_close_execute_on_t_plus_1_open",
                    "overlay_scope": "held_position_only_do_not_override_baseline_sell",
                }
            )
        return orders

    def _simulate_with_overlay(
        self,
        *,
        baseline_executed_orders: list[dict[str, Any]],
        overlay_orders: list[dict[str, Any]],
        baseline_day_rows: list[dict[str, Any]],
        daily_bars: dict[tuple[str, date], dict[str, Any]],
    ) -> list[float]:
        trade_dates = [parse_trade_date(str(row["trade_date"])) for row in baseline_day_rows]
        baseline_sell_fraction = V115PCpoIntradayTimingAwareOverlayReplayAnalyzer._baseline_sell_fraction(
            baseline_executed_orders
        )
        baseline_orders_by_exec = self._baseline_orders_by_exec_date(baseline_executed_orders)
        overlay_orders_by_exec: dict[date, list[dict[str, Any]]] = {}
        for row in overlay_orders:
            overlay_orders_by_exec.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)

        cash = self.INITIAL_CAPITAL
        positions: dict[str, int] = {}
        equity_curve: list[float] = []
        for trade_date in trade_dates:
            for row in baseline_orders_by_exec.get(trade_date, []):
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                action = str(row["action"])
                execution_price = _to_float(row["execution_price"])
                rationale = str(row.get("rationale", ""))
                if action == "buy":
                    notional = quantity * execution_price
                    cash -= notional + _costs(action="buy", notional=notional)["total_cost"]
                    positions[symbol] = positions.get(symbol, 0) + quantity
                else:
                    current_qty = positions.get(symbol, 0)
                    if current_qty <= 0:
                        continue
                    if rationale == "close_from_holding_veto":
                        sell_qty = current_qty
                    elif rationale == "reduce_from_board_state_episode":
                        fraction = baseline_sell_fraction.get((trade_date, symbol), 0.0)
                        sell_qty = int((current_qty * fraction) // 100) * 100
                        if sell_qty <= 0:
                            sell_qty = min(current_qty, 100 if current_qty >= 100 else current_qty)
                    else:
                        sell_qty = min(current_qty, quantity)
                    sell_qty = min(current_qty, sell_qty)
                    if sell_qty <= 0:
                        continue
                    notional = sell_qty * execution_price
                    cash += notional - _costs(action="sell", notional=notional)["total_cost"]
                    positions[symbol] = max(0, current_qty - sell_qty)

            for row in overlay_orders_by_exec.get(trade_date, []):
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                execution_price = _to_float(row["execution_price"])
                notional = quantity * execution_price
                cash -= notional + _costs(action="buy", notional=notional)["total_cost"]
                positions[symbol] = positions.get(symbol, 0) + quantity

            market_value = 0.0
            for symbol, quantity in positions.items():
                bar = daily_bars.get((symbol, trade_date))
                if bar is None:
                    continue
                market_value += quantity * _to_float(bar["close"])
            equity_curve.append(cash + market_value)
        return equity_curve

    def analyze(
        self,
        *,
        v113t_payload: dict[str, Any],
        v114t_payload: dict[str, Any],
        v116z_payload: dict[str, Any],
        v117a_payload: dict[str, Any],
        v117w_payload: dict[str, Any],
        v117x_payload: dict[str, Any],
        v118u_payload: dict[str, Any],
        v119l_payload: dict[str, Any],
        v119m_payload: dict[str, Any],
    ) -> V120ACpoSurvivingCandidateShadowReplayComparisonReport:
        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)
        baseline_executed_orders = list(v114t_payload.get("executed_order_rows", []))
        baseline_day_rows = list(v114t_payload.get("replay_day_rows", []))
        trade_dates = [parse_trade_date(str(row["trade_date"])) for row in baseline_day_rows]
        next_trade_date_map = self._build_next_trade_date_map(trade_dates)
        baseline_positions_eod = V115PCpoIntradayTimingAwareOverlayReplayAnalyzer._baseline_positions_eod(
            baseline_executed_orders,
            trade_dates,
        )
        baseline_next_day_sell_symbols = self._next_day_sell_symbols(executed_orders=baseline_executed_orders)
        candidate_groups = self._candidate_row_groups(
            v116z_payload=v116z_payload,
            v117a_payload=v117a_payload,
            v117w_payload=v117w_payload,
            v117x_payload=v117x_payload,
            v118u_payload=v118u_payload,
            v119l_payload=v119l_payload,
            v119m_payload=v119m_payload,
        )
        baseline_equity_curve = [_to_float(row["equity_after_close"]) for row in baseline_day_rows]
        baseline_final_equity = baseline_equity_curve[-1]

        candidate_summary_rows: list[dict[str, Any]] = []
        all_overlay_order_rows: list[dict[str, Any]] = []
        for candidate_name, raw_rows in candidate_groups.items():
            filtered_rows = self._filter_to_overlay_candidates(
                candidate_rows=raw_rows,
                baseline_positions_eod=baseline_positions_eod,
                next_trade_date_map=next_trade_date_map,
                baseline_next_day_sell_symbols=baseline_next_day_sell_symbols,
                daily_bars=daily_bars,
            )
            overlay_orders = self._build_overlay_orders(
                candidate_name=candidate_name,
                candidate_rows=filtered_rows,
                baseline_positions_eod=baseline_positions_eod,
                next_trade_date_map=next_trade_date_map,
                daily_bars=daily_bars,
                starting_cash=self.INITIAL_CAPITAL,
            )
            equity_curve = self._simulate_with_overlay(
                baseline_executed_orders=baseline_executed_orders,
                overlay_orders=overlay_orders,
                baseline_day_rows=baseline_day_rows,
                daily_bars=daily_bars,
            )
            final_equity = equity_curve[-1]
            candidate_summary_rows.append(
                {
                    "candidate_name": candidate_name,
                    "raw_signal_row_count": len(raw_rows),
                    "held_position_eligible_row_count": len(filtered_rows),
                    "executed_overlay_order_count": len(overlay_orders),
                    "overlay_symbols": sorted({str(row["symbol"]) for row in overlay_orders}),
                    "mean_signal_score_on_executed_orders": round(
                        sum(_to_float(row["signal_score"]) for row in overlay_orders) / len(overlay_orders), 6
                    )
                    if overlay_orders
                    else 0.0,
                    "mean_expectancy_proxy_3d_on_executed_orders": round(
                        sum(_to_float(row["expectancy_proxy_3d"]) for row in overlay_orders) / len(overlay_orders), 6
                    )
                    if overlay_orders
                    else 0.0,
                    "final_equity": round(final_equity, 4),
                    "delta_vs_baseline": round(final_equity - baseline_final_equity, 4),
                    "max_drawdown": _max_drawdown(equity_curve),
                    "total_overlay_transaction_cost": round(
                        sum(_to_float(row["total_cost"]) for row in overlay_orders),
                        4,
                    ),
                }
            )
            all_overlay_order_rows.extend(overlay_orders)

        summary = {
            "acceptance_posture": "freeze_v120a_cpo_surviving_candidate_shadow_replay_comparison_v1",
            "comparison_scope": "surviving_non_dead_candidates_on_unified_t_plus_1_open_shadow_replay",
            "execution_mode": "signal_on_t_close_execute_on_t_plus_1_open",
            "overlay_scope": "held_position_only_do_not_override_baseline_sell",
            "candidate_count": len(candidate_summary_rows),
            "baseline_final_equity": round(baseline_final_equity, 4),
            "baseline_max_drawdown": _max_drawdown(baseline_equity_curve),
            "recommended_next_posture": "review_shadow_replay_curves_and_order_rows_before_any_timing_aware_reinterpretation",
        }
        interpretation = [
            "V1.20A does not promote any candidate. It only answers a narrower question: if the still-alive candidates are forced into one identical execution grammar, do they retain payoff value at all?",
            "Every line uses the same conservative shadow rule: held-position-only add, no override of baseline sells, signal on T close, execute on T+1 open.",
            "This makes the comparison fairer across candidate families, even though some intraday-derived lines would later deserve richer same-session timing semantics.",
        ]
        return V120ACpoSurvivingCandidateShadowReplayComparisonReport(
            summary=summary,
            candidate_summary_rows=sorted(candidate_summary_rows, key=lambda row: row["final_equity"], reverse=True),
            overlay_order_rows=sorted(
                all_overlay_order_rows,
                key=lambda row: (str(row["candidate_name"]), str(row["execution_trade_date"]), str(row["symbol"])),
            ),
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    result: V120ACpoSurvivingCandidateShadowReplayComparisonReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / "v120a_cpo_surviving_candidate_shadow_replay_comparison_v1.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def write_order_csv(*, repo_root: Path, overlay_order_rows: list[dict[str, Any]]) -> Path:
    output_path = repo_root / "data" / "training" / "cpo_surviving_candidate_shadow_overlay_orders_v1.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "candidate_name",
        "signal_trade_date",
        "execution_trade_date",
        "symbol",
        "action",
        "signal_score",
        "signal_score_field",
        "held_qty_on_signal_close",
        "held_close_price_on_signal_date",
        "quantity",
        "execution_price",
        "notional",
        "commission",
        "stamp_tax",
        "slippage",
        "total_cost",
        "expectancy_proxy_3d",
        "max_adverse_return_3d",
        "execution_mode",
        "overlay_scope",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in overlay_order_rows:
            writer.writerow({key: row.get(key) for key in fieldnames})
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V120ACpoSurvivingCandidateShadowReplayComparisonAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v116z_payload=json.loads((repo_root / "reports" / "analysis" / "v116z_cpo_quality_side_cooled_refinement_v1.json").read_text(encoding="utf-8")),
        v117a_payload=json.loads((repo_root / "reports" / "analysis" / "v117a_cpo_quality_side_cooled_retention_v1.json").read_text(encoding="utf-8")),
        v117w_payload=json.loads((repo_root / "reports" / "analysis" / "v117w_cpo_cooling_reacceleration_false_positive_control_discovery_v1.json").read_text(encoding="utf-8")),
        v117x_payload=json.loads((repo_root / "reports" / "analysis" / "v117x_cpo_cooling_reacceleration_false_positive_control_external_audit_v1.json").read_text(encoding="utf-8")),
        v118u_payload=json.loads((repo_root / "reports" / "analysis" / "v118u_cpo_sustained_participation_non_chase_external_audit_v1.json").read_text(encoding="utf-8")),
        v119l_payload=json.loads((repo_root / "reports" / "analysis" / "v119l_cpo_participation_turnover_elg_support_discovery_v1.json").read_text(encoding="utf-8")),
        v119m_payload=json.loads((repo_root / "reports" / "analysis" / "v119m_cpo_participation_turnover_elg_support_external_audit_v1.json").read_text(encoding="utf-8")),
    )
    report_path = write_report(reports_dir=repo_root / "reports" / "analysis", result=result)
    csv_path = write_order_csv(repo_root=repo_root, overlay_order_rows=result.overlay_order_rows)
    print(report_path)
    print(csv_path)


if __name__ == "__main__":
    main()
