from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable

from a_share_quant.strategy.v115p_cpo_intraday_timing_aware_overlay_replay_v1 import (
    V115PCpoIntradayTimingAwareOverlayReplayAnalyzer,
    _to_baostock_symbol,
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


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


@dataclass(slots=True)
class V116KCpoVisibleOnlyShadowHeatTrimReviewReport:
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


class V116KCpoVisibleOnlyShadowHeatTrimReviewAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _query_bars_with_relogin(
        self,
        *,
        bs_module: Any,
        symbol: str,
        trade_date: str,
        frequency: str,
    ) -> list[dict[str, Any]]:
        rs = bs_module.query_history_k_data_plus(
            _to_baostock_symbol(symbol),
            "date,time,code,open,high,low,close,volume,amount,adjustflag",
            start_date=trade_date,
            end_date=trade_date,
            frequency=frequency,
            adjustflag="2",
        )
        if str(rs.error_code) == "10001001":
            try:
                bs_module.logout()
            except Exception:
                pass
            relogin = bs_module.login()
            if str(relogin.error_code) != "0":
                raise RuntimeError(f"baostock_relogin_failed:{relogin.error_code}:{relogin.error_msg}")
            rs = bs_module.query_history_k_data_plus(
                _to_baostock_symbol(symbol),
                "date,time,code,open,high,low,close,volume,amount,adjustflag",
                start_date=trade_date,
                end_date=trade_date,
                frequency=frequency,
                adjustflag="2",
            )
        if str(rs.error_code) != "0":
            raise RuntimeError(f"baostock_query_failed:{rs.error_code}:{rs.error_msg}")
        rows: list[dict[str, Any]] = []
        while rs.next():
            raw = rs.get_row_data()
            rows.append(
                {
                    "date": raw[0],
                    "time": raw[1],
                    "open": _to_float(raw[3]),
                }
            )
        return rows

    @staticmethod
    def _same_day_next_bar_open_from_rows(*, rows_30m: list[dict[str, Any]], checkpoint_label: str) -> float | None:
        checkpoint_hhmm = checkpoint_label.replace(":", "")
        for row in rows_30m:
            row_hhmm = str(row["time"])[8:12]
            if row_hhmm > checkpoint_hhmm:
                return _to_float(row["open"])
        return None

    def analyze(
        self,
        *,
        v113t_payload: dict[str, Any],
        v114t_payload: dict[str, Any],
        v114w_payload: dict[str, Any],
        v114x_payload: dict[str, Any],
        v116j_payload: dict[str, Any],
    ) -> V116KCpoVisibleOnlyShadowHeatTrimReviewReport:
        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)
        baseline_executed_orders = list(v114t_payload.get("executed_order_rows", []))
        baseline_day_rows = list(v114t_payload.get("replay_day_rows", []))
        baseline_day_map = {parse_trade_date(str(row["trade_date"])): row for row in baseline_day_rows}
        trade_dates = sorted(baseline_day_map.keys())
        baseline_positions_eod = V115PCpoIntradayTimingAwareOverlayReplayAnalyzer._baseline_positions_eod(
            baseline_executed_orders, trade_dates
        )
        baseline_sell_fraction = V115PCpoIntradayTimingAwareOverlayReplayAnalyzer._baseline_sell_fraction(
            baseline_executed_orders
        )
        repaired_miss_rows = list(v114w_payload.get("top_opportunity_miss_rows", []))
        miss_day_map = {str(row["trade_date"]): row for row in repaired_miss_rows}

        strong_floor = 0.3
        two_line_floor = 0.45
        for row in list(v114x_payload.get("exposure_floor_rows", [])):
            board_state = str(row.get("board_state"))
            if board_state == "strong_board_with_one_high_probability_line":
                strong_floor = _to_float(row.get("minimum_target_gross_exposure"), strong_floor)
            elif board_state == "strong_board_with_two_or_more_credible_lines":
                two_line_floor = _to_float(row.get("minimum_target_gross_exposure"), two_line_floor)

        timing_rows = list(v116j_payload.get("timing_rows", []))
        checkpoint_rows = list(v116j_payload.get("checkpoint_rows", []))
        checkpoint_map: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in checkpoint_rows:
            checkpoint_map.setdefault((str(row["signal_trade_date"]), str(row["symbol"])), []).append(row)
        for rows in checkpoint_map.values():
            rows.sort(key=lambda row: str(row["checkpoint"]))

        def has_pass(row_key: tuple[str, str], checkpoint: str) -> bool:
            for row in checkpoint_map.get(row_key, []):
                if str(row["checkpoint"]) == checkpoint:
                    return _to_bool(row.get("passes_pc1_or_pc2_q_0p25"))
            return False

        def earliest_late_checkpoint(row_key: tuple[str, str]) -> str | None:
            for checkpoint in ("14:00", "14:30"):
                if has_pass(row_key, checkpoint):
                    return checkpoint
            return None

        variants: list[tuple[str, Callable[[dict[str, Any]], bool], Callable[[tuple[str, str]], str | None], float, float]] = [
            (
                "earliest_visible_reference",
                lambda row: True,
                lambda key: next(
                    (str(r["earliest_visible_checkpoint"]) for r in timing_rows if (str(r["signal_trade_date"]), str(r["symbol"])) == key),
                    None,
                ),
                0.5,
                0.5,
            ),
            (
                "late_persistence_full",
                lambda row: earliest_late_checkpoint((str(row["signal_trade_date"]), str(row["symbol"]))) is not None,
                earliest_late_checkpoint,
                0.5,
                0.5,
            ),
            (
                "double_confirm_late_full",
                lambda row: (
                    has_pass((str(row["signal_trade_date"]), str(row["symbol"])), "10:30")
                    and has_pass((str(row["signal_trade_date"]), str(row["symbol"])), "11:00")
                    and earliest_late_checkpoint((str(row["signal_trade_date"]), str(row["symbol"]))) is not None
                ),
                earliest_late_checkpoint,
                0.5,
                0.5,
            ),
            (
                "late_persistence_quarter",
                lambda row: earliest_late_checkpoint((str(row["signal_trade_date"]), str(row["symbol"]))) is not None,
                earliest_late_checkpoint,
                0.25,
                0.35,
            ),
            (
                "double_confirm_late_quarter",
                lambda row: (
                    has_pass((str(row["signal_trade_date"]), str(row["symbol"])), "10:30")
                    and has_pass((str(row["signal_trade_date"]), str(row["symbol"])), "11:00")
                    and earliest_late_checkpoint((str(row["signal_trade_date"]), str(row["symbol"]))) is not None
                ),
                earliest_late_checkpoint,
                0.25,
                0.35,
            ),
        ]

        baseline_equity_curve = [_to_float(row.get("equity_after_close")) for row in baseline_day_rows]
        variant_rows: list[dict[str, Any]] = []
        all_overlay_rows: list[dict[str, Any]] = []
        import baostock as bs

        login_result = bs.login()
        if str(login_result.error_code) != "0":
            raise RuntimeError(f"baostock_login_failed:{login_result.error_code}:{login_result.error_msg}")
        try:
            bars_30m_cache: dict[tuple[str, str], list[dict[str, Any]]] = {}
            for row in timing_rows:
                signal_trade_date = str(row["signal_trade_date"])
                symbol = str(row["symbol"])
                key = (signal_trade_date, symbol)
                if key not in bars_30m_cache:
                    bars_30m_cache[key] = self._query_bars_with_relogin(
                        bs_module=bs,
                        symbol=symbol,
                        trade_date=signal_trade_date,
                        frequency="30",
                    )

            for variant_name, predicate, checkpoint_selector, overlay_fill_fraction, per_symbol_cap_ratio in variants:
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

                    signal_trade_date = str(trade_date)
                    miss_row = miss_day_map.get(signal_trade_date)
                    baseline_day = baseline_day_map[trade_date]
                    valid_hits: list[dict[str, Any]] = []
                    if miss_row is not None:
                        for row in timing_rows:
                            if str(row["signal_trade_date"]) != signal_trade_date:
                                continue
                            if str(row.get("timing_bucket")) != "intraday_same_session":
                                continue
                            if not predicate(row):
                                continue
                            symbol = str(row["symbol"])
                            held_qty = baseline_positions_eod.get((trade_date, symbol), 0)
                            if held_qty <= 0:
                                continue
                            close_row = daily_bars.get((symbol, trade_date))
                            if close_row is None:
                                continue
                            checkpoint_label = checkpoint_selector((signal_trade_date, symbol))
                            if checkpoint_label is None:
                                continue
                            execution_price = self._same_day_next_bar_open_from_rows(
                                rows_30m=bars_30m_cache.get((signal_trade_date, symbol), []),
                                checkpoint_label=checkpoint_label,
                            )
                            if execution_price is None or execution_price <= 0:
                                continue
                            held_value = held_qty * _to_float(close_row["close"])
                            valid_hits.append(
                                {
                                    "symbol": symbol,
                                    "held_value": held_value,
                                    "execution_price": execution_price,
                                    "timing_checkpoint": checkpoint_label,
                                    "visible_pc1_score": _to_float(row.get("visible_pc1_score")),
                                    "visible_pc2_score": _to_float(row.get("visible_pc2_score")),
                                }
                            )

                    if valid_hits:
                        signal_equity = _to_float(baseline_day.get("equity_after_close"))
                        current_exposure = _to_float(miss_row.get("gross_exposure_after_close"))
                        board_avg_return = _to_float(miss_row.get("board_avg_return"))
                        board_breadth = _to_float(miss_row.get("board_breadth"))
                        target_floor = two_line_floor if board_avg_return >= 0.05 and board_breadth >= 0.8 else strong_floor
                        gap_to_floor = max(target_floor - current_exposure, 0.0)
                        if signal_equity > 0 and gap_to_floor > 0:
                            gross_pool = signal_equity * gap_to_floor * overlay_fill_fraction
                            per_hit_pool = gross_pool / len(valid_hits)
                            for hit in valid_hits:
                                capped_notional = min(
                                    per_hit_pool,
                                    hit["held_value"] * per_symbol_cap_ratio,
                                    100_000.0,
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
                                        "signal_trade_date": signal_trade_date,
                                        "execution_trade_date": signal_trade_date,
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
                                        "visible_pc1_score": round(hit["visible_pc1_score"], 6),
                                        "visible_pc2_score": round(hit["visible_pc2_score"], 6),
                                        "overlay_posture": "visible_only_shadow_heat_trim_candidate",
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
                        "candidate_signal_count": sum(1 for row in timing_rows if predicate(row) and str(row.get("timing_bucket")) == "intraday_same_session"),
                        "executed_order_count": len(overlay_order_rows),
                        "overlay_fill_fraction": overlay_fill_fraction,
                        "per_symbol_position_add_cap_ratio": per_symbol_cap_ratio,
                        "final_equity": round(equity_curve[-1], 4),
                        "equity_delta_vs_baseline": round(equity_curve[-1] - baseline_equity_curve[-1], 4),
                        "max_drawdown": _max_drawdown(equity_curve),
                        "overlay_total_transaction_cost": round(sum(_to_float(row["total_cost"]) for row in overlay_order_rows), 4),
                    }
                )
                all_overlay_rows.extend(overlay_order_rows)
        finally:
            try:
                bs.logout()
            except Exception:
                pass

        best_variant = max(variant_rows, key=lambda row: _to_float(row["final_equity"])) if variant_rows else None
        cleanest_variant = min(
            (row for row in variant_rows if int(row["executed_order_count"]) > 0),
            key=lambda row: _to_float(row["max_drawdown"]),
            default=None,
        )
        summary = {
            "acceptance_posture": "freeze_v116k_cpo_visible_only_shadow_heat_trim_review_v1",
            "baseline_final_equity": round(baseline_equity_curve[-1], 4),
            "variant_count": len(variant_rows),
            "best_variant_by_equity": None if best_variant is None else str(best_variant["variant_name"]),
            "cleanest_executing_variant": None if cleanest_variant is None else str(cleanest_variant["variant_name"]),
            "recommended_next_posture": "select_one_cooled_visible_only_shadow_candidate_for_retention_not_for_promotion",
        }
        interpretation = [
            "V1.16K tests heat-trimmed variants of the broader visible-only shadow replay rather than continuing to widen the hot `pc1_or_pc2_q_0p25` line unchecked.",
            "The variants only change visible checkpoint confirmation timing and sizing aggression; they do not introduce future labels or admission authority.",
            "This run exists to find a cooler shadow candidate, not to create a new promotable law.",
        ]
        return V116KCpoVisibleOnlyShadowHeatTrimReviewReport(
            summary=summary,
            variant_rows=variant_rows,
            overlay_order_rows=all_overlay_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V116KCpoVisibleOnlyShadowHeatTrimReviewReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V116KCpoVisibleOnlyShadowHeatTrimReviewAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v114w_payload=json.loads((repo_root / "reports" / "analysis" / "v114w_cpo_under_exposure_attribution_repaired_v1.json").read_text(encoding="utf-8")),
        v114x_payload=json.loads((repo_root / "reports" / "analysis" / "v114x_cpo_probability_expectancy_sizing_framework_repaired_v1.json").read_text(encoding="utf-8")),
        v116j_payload=json.loads((repo_root / "reports" / "analysis" / "v116j_cpo_visible_only_broader_shadow_replay_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v116k_cpo_visible_only_shadow_heat_trim_review_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
