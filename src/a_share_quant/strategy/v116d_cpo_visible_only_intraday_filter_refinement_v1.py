from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable

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


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    idx = (len(sorted_values) - 1) * q
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_values[lo]
    weight = idx - lo
    return sorted_values[lo] * (1 - weight) + sorted_values[hi] * weight


@dataclass(slots=True)
class V116DCpoVisibleOnlyIntradayFilterRefinementReport:
    summary: dict[str, Any]
    threshold_rows: list[dict[str, Any]]
    variant_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "threshold_rows": self.threshold_rows,
            "variant_rows": self.variant_rows,
            "interpretation": self.interpretation,
        }


class V116DCpoVisibleOnlyIntradayFilterRefinementAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _baseline_positions_eod(executed_orders: list[dict[str, Any]], trade_dates: list[date]) -> dict[tuple[date, str], int]:
        return V115PCpoIntradayTimingAwareOverlayReplayAnalyzer._baseline_positions_eod(executed_orders, trade_dates)

    @staticmethod
    def _baseline_sell_fraction(executed_orders: list[dict[str, Any]]) -> dict[tuple[date, str], float]:
        return V115PCpoIntradayTimingAwareOverlayReplayAnalyzer._baseline_sell_fraction(executed_orders)

    def _run_variant(
        self,
        *,
        variant_name: str,
        predicate: Callable[[dict[str, Any]], bool],
        enriched_rows: list[dict[str, Any]],
        baseline_executed_orders: list[dict[str, Any]],
        baseline_day_rows: list[dict[str, Any]],
        baseline_day_map: dict[date, dict[str, Any]],
        trade_dates: list[date],
        baseline_positions_eod: dict[tuple[date, str], int],
        baseline_sell_fraction: dict[tuple[date, str], float],
        daily_bars: dict[tuple[str, date], dict[str, Any]],
        analyzer: V115PCpoIntradayTimingAwareOverlayReplayAnalyzer,
    ) -> dict[str, Any]:
        overlay_fill_fraction = 0.5
        per_symbol_position_add_cap_ratio = 0.5
        max_extra_notional_per_symbol = 100_000.0
        gross_floor = 0.45

        baseline_equity_curve = [_to_float(row.get("equity_after_close")) for row in baseline_day_rows]
        overlay_orders_by_signal: dict[date, list[dict[str, Any]]] = {}

        for row in enriched_rows:
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
            execution_price = analyzer._same_day_next_bar_open(
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
                    "visible_pc1_score": _to_float(row.get("visible_pc1_score")),
                    "visible_pc2_score": _to_float(row.get("visible_pc2_score")),
                }
            )

        cash = 1_000_000.0
        positions: dict[str, int] = {}
        baseline_orders_by_exec: dict[date, list[dict[str, Any]]] = {}
        for row in baseline_executed_orders:
            baseline_orders_by_exec.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)
        executed_order_count = 0
        overlay_total_cost = 0.0
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
                    executed_order_count += 1
                    overlay_total_cost += costs["total_cost"]

            market_value = 0.0
            for symbol, qty in positions.items():
                bar = daily_bars.get((symbol, trade_date))
                if bar is None:
                    continue
                market_value += qty * _to_float(bar["close"])
            equity_curve.append(cash + market_value)

        return {
            "variant_name": variant_name,
            "candidate_signal_count": len([row for row in enriched_rows if predicate(row)]),
            "executed_order_count": executed_order_count,
            "final_equity": round(equity_curve[-1], 4),
            "equity_delta_vs_baseline": round(equity_curve[-1] - baseline_equity_curve[-1], 4),
            "max_drawdown": _max_drawdown(equity_curve),
            "overlay_total_transaction_cost": round(overlay_total_cost, 4),
        }

    def analyze(
        self,
        *,
        v113t_payload: dict[str, Any],
        v114t_payload: dict[str, Any],
        v115q_payload: dict[str, Any],
    ) -> V116DCpoVisibleOnlyIntradayFilterRefinementReport:
        import baostock as bs

        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)
        baseline_executed_orders = list(v114t_payload.get("executed_order_rows", []))
        baseline_day_rows = list(v114t_payload.get("replay_day_rows", []))
        baseline_day_map = {parse_trade_date(str(row["trade_date"])): row for row in baseline_day_rows}
        trade_dates = sorted(baseline_day_map.keys())
        baseline_positions_eod = self._baseline_positions_eod(baseline_executed_orders, trade_dates)
        baseline_sell_fraction = self._baseline_sell_fraction(baseline_executed_orders)
        candidate_rows = [row for row in list(v115q_payload.get("timing_rows", [])) if str(row.get("timing_bucket")) == "intraday_same_session"]
        checkpoint_rows = [
            row for row in list(v115q_payload.get("checkpoint_rows", [])) if str(row.get("checkpoint")) == "10:30"
        ]
        checkpoint_map = {(str(row["signal_trade_date"]), str(row["symbol"])): row for row in checkpoint_rows}

        enriched_rows = []
        for row in candidate_rows:
            cp = checkpoint_map[(str(row["signal_trade_date"]), str(row["symbol"]))]
            enriched_rows.append(
                {
                    **row,
                    "visible_pc1_score": _to_float(cp.get("pc1_score")),
                    "visible_pc2_score": _to_float(cp.get("pc2_score")),
                }
            )

        pc1_values = sorted(_to_float(row["visible_pc1_score"]) for row in enriched_rows)
        pc2_values = sorted(_to_float(row["visible_pc2_score"]) for row in enriched_rows)
        quantiles = [0.2, 0.25, 0.33, 0.4, 0.5]
        threshold_rows = [
            {
                "quantile": q,
                "pc1_low_threshold": round(_quantile(pc1_values, q), 6),
                "pc2_low_threshold": round(_quantile(pc2_values, q), 6),
            }
            for q in quantiles
        ]

        filters: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [("all_intraday_strict_visible", lambda row: True)]
        for threshold_row in threshold_rows:
            q = _to_float(threshold_row["quantile"])
            q_tag = str(q).replace(".", "p")
            pc1_low = _to_float(threshold_row["pc1_low_threshold"])
            pc2_low = _to_float(threshold_row["pc2_low_threshold"])
            filters.extend(
                [
                    (f"pc1_only_q_{q_tag}", lambda row, pc1_low=pc1_low: _to_float(row["visible_pc1_score"]) <= pc1_low),
                    (f"pc2_only_q_{q_tag}", lambda row, pc2_low=pc2_low: _to_float(row["visible_pc2_score"]) <= pc2_low),
                    (
                        f"pc1_or_pc2_q_{q_tag}",
                        lambda row, pc1_low=pc1_low, pc2_low=pc2_low: _to_float(row["visible_pc1_score"]) <= pc1_low
                        or _to_float(row["visible_pc2_score"]) <= pc2_low,
                    ),
                    (
                        f"pc1_and_pc2_q_{q_tag}",
                        lambda row, pc1_low=pc1_low, pc2_low=pc2_low: _to_float(row["visible_pc1_score"]) <= pc1_low
                        and _to_float(row["visible_pc2_score"]) <= pc2_low,
                    ),
                ]
            )

        login_result = bs.login()
        if str(login_result.error_code) != "0":
            raise RuntimeError(f"baostock_login_failed:{login_result.error_code}:{login_result.error_msg}")
        variant_rows: list[dict[str, Any]] = []
        try:
            analyzer = V115PCpoIntradayTimingAwareOverlayReplayAnalyzer(repo_root=self.repo_root)
            for variant_name, predicate in filters:
                variant_rows.append(
                    self._run_variant(
                        variant_name=variant_name,
                        predicate=predicate,
                        enriched_rows=enriched_rows,
                        baseline_executed_orders=baseline_executed_orders,
                        baseline_day_rows=baseline_day_rows,
                        baseline_day_map=baseline_day_map,
                        trade_dates=trade_dates,
                        baseline_positions_eod=baseline_positions_eod,
                        baseline_sell_fraction=baseline_sell_fraction,
                        daily_bars=daily_bars,
                        analyzer=analyzer,
                    )
                )
        finally:
            try:
                bs.logout()
            except Exception:
                pass

        best_equity = max(variant_rows, key=lambda row: _to_float(row["final_equity"])) if variant_rows else None
        best_clean = min(
            [row for row in variant_rows if _to_float(row["executed_order_count"]) > 0],
            key=lambda row: (_to_float(row["max_drawdown"]), -_to_float(row["final_equity"])),
        ) if any(_to_float(row["executed_order_count"]) > 0 for row in variant_rows) else None
        summary = {
            "acceptance_posture": "freeze_v116d_cpo_visible_only_intraday_filter_refinement_v1",
            "baseline_final_equity": round(_to_float(baseline_day_rows[-1]["equity_after_close"]), 4),
            "variant_count": len(variant_rows),
            "best_variant_by_equity": None if best_equity is None else str(best_equity["variant_name"]),
            "cleanest_executing_variant": None if best_clean is None else str(best_clean["variant_name"]),
            "recommended_next_posture": "carry_forward_visible_only_executing_variants_and_prepare_next_three_run_adversarial_review",
        }
        interpretation = [
            "V1.16D refines visible-only intraday filters by sweeping point-in-time-visible pc1/pc2 low-threshold variants, with no future labels permitted.",
            "The goal is not promotion, but to identify whether a cleaner executing candidate exists between all-strict-visible and overly sparse no-trade variants.",
            "Any resulting winner remains candidate-only until it survives the next three-run adversarial review cadence.",
        ]
        return V116DCpoVisibleOnlyIntradayFilterRefinementReport(
            summary=summary,
            threshold_rows=threshold_rows,
            variant_rows=variant_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V116DCpoVisibleOnlyIntradayFilterRefinementReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116DCpoVisibleOnlyIntradayFilterRefinementAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v115q_payload=json.loads((repo_root / "reports" / "analysis" / "v115q_cpo_broader_strict_add_timing_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116d_cpo_visible_only_intraday_filter_refinement_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
