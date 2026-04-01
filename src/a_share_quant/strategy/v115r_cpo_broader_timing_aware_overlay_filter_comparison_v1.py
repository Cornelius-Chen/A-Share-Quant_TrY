from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v115n_cpo_intraday_strict_band_held_position_overlay_replay_v1 import (
    _costs,
    _load_daily_bars,
    _max_drawdown,
)
from a_share_quant.strategy.v115p_cpo_intraday_timing_aware_overlay_replay_v1 import (
    V115PCpoIntradayTimingAwareOverlayReplayAnalyzer,
    parse_trade_date,
)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass(slots=True)
class V115RCpoBroaderTimingAwareOverlayFilterComparisonReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    overlay_order_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "overlay_order_rows": self.overlay_order_rows,
            "interpretation": self.interpretation,
        }


class V115RCpoBroaderTimingAwareOverlayFilterComparisonAnalyzer:
    FILTERS = {
        "all_strict_add_context": lambda row: True,
        "positive_expectancy_only": lambda row: _to_float(row.get("expectancy_proxy_3d")) > 0,
        "action_favored_only": lambda row: bool(row.get("action_favored_3d")),
        "positive_and_favored": lambda row: _to_float(row.get("expectancy_proxy_3d")) > 0 and bool(row.get("action_favored_3d")),
    }

    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _baseline_positions_eod(executed_orders: list[dict[str, Any]], trade_dates: list[date]) -> dict[tuple[date, str], int]:
        return V115PCpoIntradayTimingAwareOverlayReplayAnalyzer._baseline_positions_eod(executed_orders, trade_dates)

    @staticmethod
    def _baseline_sell_fraction(executed_orders: list[dict[str, Any]]) -> dict[tuple[date, str], float]:
        return V115PCpoIntradayTimingAwareOverlayReplayAnalyzer._baseline_sell_fraction(executed_orders)

    def _same_day_next_bar_open(self, *, symbol: str, trade_date: str, checkpoint_label: str) -> float | None:
        import baostock as bs

        analyzer = V115PCpoIntradayTimingAwareOverlayReplayAnalyzer(repo_root=self.repo_root)
        login_result = bs.login()
        if str(login_result.error_code) != "0":
            return None
        try:
            return analyzer._same_day_next_bar_open(
                symbol=symbol,
                trade_date=trade_date,
                checkpoint_label=checkpoint_label,
            )
        finally:
            try:
                bs.logout()
            except Exception:
                pass

    def analyze(
        self,
        *,
        v113t_payload: dict[str, Any],
        v114t_payload: dict[str, Any],
        v115q_payload: dict[str, Any],
    ) -> V115RCpoBroaderTimingAwareOverlayFilterComparisonReport:
        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)
        baseline_executed_orders = list(v114t_payload.get("executed_order_rows", []))
        baseline_day_rows = list(v114t_payload.get("replay_day_rows", []))
        baseline_day_map = {parse_trade_date(str(row["trade_date"])): row for row in baseline_day_rows}
        trade_dates = sorted(baseline_day_map.keys())
        baseline_positions_eod = self._baseline_positions_eod(baseline_executed_orders, trade_dates)
        baseline_sell_fraction = self._baseline_sell_fraction(baseline_executed_orders)
        candidate_rows = [row for row in list(v115q_payload.get("timing_rows", [])) if str(row.get("timing_bucket")) == "intraday_same_session"]

        overlay_fill_fraction = 0.5
        per_symbol_position_add_cap_ratio = 0.5
        max_extra_notional_per_symbol = 100_000.0
        gross_floor = 0.45

        baseline_equity_curve = [_to_float(row.get("equity_after_close")) for row in baseline_day_rows]
        variant_rows: list[dict[str, Any]] = []
        all_overlay_rows: list[dict[str, Any]] = []

        for variant_name, predicate in self.FILTERS.items():
            overlay_orders_by_signal: dict[date, list[dict[str, Any]]] = {}
            for row in candidate_rows:
                if not predicate(row):
                    continue
                signal_trade_date = parse_trade_date(str(row["signal_trade_date"]))
                symbol = str(row["symbol"])
                held_qty = baseline_positions_eod.get((signal_trade_date, symbol), 0)
                if held_qty <= 0:
                    continue
                baseline_day = baseline_day_map.get(signal_trade_date)
                close_row = daily_bars.get((symbol, signal_trade_date))
                if baseline_day is None or close_row is None:
                    continue
                execution_price = self._same_day_next_bar_open(
                    symbol=symbol,
                    trade_date=str(signal_trade_date),
                    checkpoint_label=str(row["earliest_strict_checkpoint"]),
                )
                if execution_price is None or execution_price <= 0:
                    continue
                held_value = held_qty * _to_float(close_row["close"])
                signal_equity = _to_float(baseline_day.get("equity_after_close"))
                current_exposure = _to_float(baseline_day.get("gross_exposure_after_close"))
                gap_to_floor = max(gross_floor - current_exposure, 0.0)
                if signal_equity <= 0 or gap_to_floor <= 0:
                    continue
                overlay_orders_by_signal.setdefault(signal_trade_date, []).append(
                    {
                        "signal_trade_date": str(signal_trade_date),
                        "execution_trade_date": str(signal_trade_date),
                        "symbol": symbol,
                        "execution_price": execution_price,
                        "held_value": held_value,
                        "timing_checkpoint": str(row["earliest_strict_checkpoint"]),
                        "expectancy_proxy_3d": _to_float(row.get("expectancy_proxy_3d")),
                        "action_favored_3d": bool(row.get("action_favored_3d")),
                        "variant_name": variant_name,
                        "gross_exposure_gap_to_floor": gap_to_floor,
                    }
                )

            cash = 1_000_000.0
            positions: dict[str, int] = {}
            baseline_orders_by_exec: dict[date, list[dict[str, Any]]] = {}
            for row in baseline_executed_orders:
                baseline_orders_by_exec.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)
            overlay_order_rows: list[dict[str, Any]] = []
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

                todays_hits = overlay_orders_by_signal.get(trade_date, [])
                if todays_hits:
                    baseline_day = baseline_day_map[trade_date]
                    signal_equity = _to_float(baseline_day.get("equity_after_close"))
                    gross_pool = signal_equity * max(gross_floor - _to_float(baseline_day.get("gross_exposure_after_close")), 0.0) * overlay_fill_fraction
                    per_hit_pool = gross_pool / len(todays_hits) if todays_hits else 0.0
                    for hit in todays_hits:
                        capped_notional = min(
                            per_hit_pool,
                            hit["held_value"] * per_symbol_position_add_cap_ratio,
                            max_extra_notional_per_symbol,
                        )
                        quantity = int((capped_notional / hit["execution_price"]) // 100) * 100
                        affordable_qty = int(cash // (hit["execution_price"] * 1.0018))
                        affordable_qty = (affordable_qty // 100) * 100
                        quantity = min(quantity, max(0, affordable_qty))
                        if quantity <= 0:
                            continue
                        notional = quantity * hit["execution_price"]
                        costs = _costs(action="buy", notional=notional)
                        cash -= notional + costs["total_cost"]
                        positions[hit["symbol"]] = positions.get(hit["symbol"], 0) + quantity
                        overlay_order_rows.append(
                            {
                                "variant_name": variant_name,
                                "signal_trade_date": hit["signal_trade_date"],
                                "execution_trade_date": hit["execution_trade_date"],
                                "symbol": hit["symbol"],
                                "action": "buy",
                                "quantity": quantity,
                                "execution_price": round(hit["execution_price"], 4),
                                "notional": round(notional, 4),
                                "commission": costs["commission"],
                                "stamp_tax": costs["stamp_tax"],
                                "slippage": costs["slippage"],
                                "total_cost": costs["total_cost"],
                                "timing_bucket": "intraday_same_session",
                                "timing_checkpoint": hit["timing_checkpoint"],
                                "expectancy_proxy_3d": round(hit["expectancy_proxy_3d"], 6),
                                "action_favored_3d": hit["action_favored_3d"],
                                "overlay_posture": "broader_strict_intraday_timing_aware_add_only",
                            }
                        )

                market_value = 0.0
                for symbol, qty in positions.items():
                    bar = daily_bars.get((symbol, trade_date))
                    if bar is None:
                        continue
                    market_value += qty * _to_float(bar["close"])
                equity_curve.append(cash + market_value)

            variant_rows.append(
                {
                    "variant_name": variant_name,
                    "candidate_signal_count": len([row for row in candidate_rows if predicate(row)]),
                    "executed_order_count": len(overlay_order_rows),
                    "final_equity": round(equity_curve[-1], 4),
                    "equity_delta_vs_baseline": round(equity_curve[-1] - baseline_equity_curve[-1], 4),
                    "max_drawdown": _max_drawdown(equity_curve),
                    "overlay_total_transaction_cost": round(sum(_to_float(row["total_cost"]) for row in overlay_order_rows), 4),
                }
            )
            all_overlay_rows.extend(overlay_order_rows)

        best_variant = max(variant_rows, key=lambda row: _to_float(row["final_equity"])) if variant_rows else None
        cleanest_variant = min(variant_rows, key=lambda row: _to_float(row["max_drawdown"])) if variant_rows else None
        summary = {
            "acceptance_posture": "freeze_v115r_cpo_broader_timing_aware_overlay_filter_comparison_v1",
            "baseline_final_equity": round(baseline_equity_curve[-1], 4),
            "variant_count": len(variant_rows),
            "best_variant_by_equity": None if best_variant is None else str(best_variant["variant_name"]),
            "cleanest_variant_by_drawdown": None if cleanest_variant is None else str(cleanest_variant["variant_name"]),
            "recommended_next_posture": "retain_filtered_timing_aware_overlay_variants_in_parallel_and_do_not_promote_until_broader_revalidation",
        }
        interpretation = [
            "V1.15R compares broader timing-aware overlay filters on top of the repaired replay, instead of relying only on the original top-miss slice.",
            "The comparison keeps the same safety rails: held-position only, no new admissions, no sell-side override, and timing-aware same-session next-bar execution only for intraday-visible strict hits.",
            "This is a filter comparison, not a promotion step.",
        ]
        return V115RCpoBroaderTimingAwareOverlayFilterComparisonReport(
            summary=summary,
            variant_rows=variant_rows,
            overlay_order_rows=all_overlay_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V115RCpoBroaderTimingAwareOverlayFilterComparisonReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115RCpoBroaderTimingAwareOverlayFilterComparisonAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v115q_payload=json.loads((repo_root / "reports" / "analysis" / "v115q_cpo_broader_strict_add_timing_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115r_cpo_broader_timing_aware_overlay_filter_comparison_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
