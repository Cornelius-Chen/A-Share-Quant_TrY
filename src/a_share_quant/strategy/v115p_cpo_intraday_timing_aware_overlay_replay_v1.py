from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v115n_cpo_intraday_strict_band_held_position_overlay_replay_v1 import (
    _costs,
    _load_daily_bars,
    _max_drawdown,
)


def parse_trade_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_baostock_symbol(symbol: str) -> str:
    symbol = str(symbol).strip()
    if symbol.startswith(("600", "601", "603", "605", "688", "689", "900")):
        return f"sh.{symbol}"
    return f"sz.{symbol}"


@dataclass(slots=True)
class V115PCpoIntradayTimingAwareOverlayReplayReport:
    summary: dict[str, Any]
    overlay_order_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "overlay_order_rows": self.overlay_order_rows,
            "interpretation": self.interpretation,
        }


class V115PCpoIntradayTimingAwareOverlayReplayAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _baseline_positions_eod(executed_orders: list[dict[str, Any]], trade_dates: list[date]) -> dict[tuple[date, str], int]:
        positions: dict[str, int] = {}
        by_day: dict[tuple[date, str], int] = {}
        rows_by_date: dict[date, list[dict[str, Any]]] = {}
        for row in executed_orders:
            rows_by_date.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)
        symbols = sorted({str(row["symbol"]) for row in executed_orders})
        for trade_date in trade_dates:
            for row in rows_by_date.get(trade_date, []):
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                if str(row["action"]) == "buy":
                    positions[symbol] = positions.get(symbol, 0) + quantity
                else:
                    positions[symbol] = max(0, positions.get(symbol, 0) - quantity)
            for symbol in symbols:
                by_day[(trade_date, symbol)] = positions.get(symbol, 0)
        return by_day

    @staticmethod
    def _baseline_sell_fraction(executed_orders: list[dict[str, Any]]) -> dict[tuple[date, str], float]:
        positions: dict[str, int] = {}
        fractions: dict[tuple[date, str], float] = {}
        ordered = sorted(
            executed_orders,
            key=lambda row: (parse_trade_date(str(row["execution_trade_date"])), str(row["symbol"]), str(row["action"])),
        )
        for row in ordered:
            exec_date = parse_trade_date(str(row["execution_trade_date"]))
            symbol = str(row["symbol"])
            action = str(row["action"])
            quantity = int(row["quantity"])
            if action == "buy":
                positions[symbol] = positions.get(symbol, 0) + quantity
                continue
            before_qty = positions.get(symbol, 0)
            fraction = 0.0 if before_qty <= 0 else min(quantity / before_qty, 1.0)
            fractions[(exec_date, symbol)] = fraction
            positions[symbol] = max(0, before_qty - quantity)
        return fractions

    def _same_day_next_bar_open(self, *, symbol: str, trade_date: str, checkpoint_label: str) -> float | None:
        import baostock as bs

        hhmm = checkpoint_label.replace(":", "")
        rs = bs.query_history_k_data_plus(
            _to_baostock_symbol(symbol),
            "date,time,code,open,high,low,close,volume,amount,adjustflag",
            start_date=trade_date,
            end_date=trade_date,
            frequency="30",
            adjustflag="2",
        )
        if str(rs.error_code) != "0":
            return None
        rows: list[dict[str, Any]] = []
        while rs.next():
            raw = rs.get_row_data()
            rows.append(
                {
                    "time": raw[1],
                    "open": _to_float(raw[3]),
                }
            )
        for row in rows:
            row_hhmm = str(row["time"])[8:12]
            if row_hhmm > hhmm:
                return _to_float(row["open"])
        return None

    def analyze(
        self,
        *,
        v113t_payload: dict[str, Any],
        v114t_payload: dict[str, Any],
        v115m_payload: dict[str, Any],
        v115o_payload: dict[str, Any],
    ) -> V115PCpoIntradayTimingAwareOverlayReplayReport:
        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)
        baseline_executed_orders = list(v114t_payload.get("executed_order_rows", []))
        baseline_day_rows = list(v114t_payload.get("replay_day_rows", []))
        baseline_day_map = {
            parse_trade_date(str(row["trade_date"])): row
            for row in baseline_day_rows
        }
        trade_dates = sorted(baseline_day_map.keys())
        baseline_positions_eod = self._baseline_positions_eod(baseline_executed_orders, trade_dates)
        baseline_sell_fraction = self._baseline_sell_fraction(baseline_executed_orders)
        miss_days = {
            parse_trade_date(str(row["trade_date"])): row
            for row in list(v115m_payload.get("miss_day_uplift_rows", []))
        }
        timing_rows = {
            (str(row["signal_trade_date"]), str(row["symbol"])): row
            for row in list(v115o_payload.get("timing_rows", []))
        }

        overlay_fill_fraction = 0.5
        per_symbol_position_add_cap_ratio = 0.5
        max_extra_notional_per_symbol = 100_000.0

        overlay_order_rows: list[dict[str, Any]] = []
        cash = 1_000_000.0
        positions: dict[str, int] = {}

        baseline_orders_by_exec: dict[date, list[dict[str, Any]]] = {}
        for row in baseline_executed_orders:
            baseline_orders_by_exec.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)

        import baostock as bs

        login_result = bs.login()
        if str(login_result.error_code) != "0":
            raise RuntimeError(f"baostock_login_failed:{login_result.error_code}:{login_result.error_msg}")
        try:
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

                signal_trade_date = trade_date
                miss_row = miss_days.get(signal_trade_date)
                if miss_row is None:
                    continue
                baseline_day = baseline_day_map[signal_trade_date]
                signal_equity = _to_float(baseline_day.get("equity_after_close"))
                gap_to_floor = _to_float(miss_row.get("gross_exposure_gap_to_floor"))
                if signal_equity <= 0 or gap_to_floor <= 0:
                    continue
                valid_hits: list[dict[str, Any]] = []
                symbols = str(miss_row.get("strict_hit_symbols", "")).split(",")
                for symbol in [s for s in symbols if s]:
                    timing = timing_rows.get((str(signal_trade_date), symbol))
                    if timing is None or str(timing.get("timing_bucket")) != "intraday_same_session":
                        continue
                    held_qty = baseline_positions_eod.get((signal_trade_date, symbol), 0)
                    if held_qty <= 0:
                        continue
                    close_row = daily_bars.get((symbol, signal_trade_date))
                    if close_row is None:
                        continue
                    execution_price = self._same_day_next_bar_open(
                        symbol=symbol,
                        trade_date=str(signal_trade_date),
                        checkpoint_label=str(timing["earliest_strict_checkpoint"]),
                    )
                    if execution_price is None or execution_price <= 0:
                        continue
                    held_value = held_qty * _to_float(close_row["close"])
                    valid_hits.append(
                        {
                            "symbol": symbol,
                            "held_value": held_value,
                            "execution_price": execution_price,
                            "checkpoint": str(timing["earliest_strict_checkpoint"]),
                        }
                    )
                if not valid_hits:
                    continue
                gross_pool = signal_equity * gap_to_floor * overlay_fill_fraction
                per_hit_pool = gross_pool / len(valid_hits)
                for hit in valid_hits:
                    capped_notional = min(per_hit_pool, hit["held_value"] * per_symbol_position_add_cap_ratio, max_extra_notional_per_symbol)
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
                            "signal_trade_date": str(signal_trade_date),
                            "execution_trade_date": str(signal_trade_date),
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
                            "timing_checkpoint": hit["checkpoint"],
                            "overlay_posture": "strict_intraday_timing_aware_add_only",
                        }
                    )
        finally:
            try:
                bs.logout()
            except Exception:
                pass

        equity_curve: list[float] = []
        cash_for_curve = 1_000_000.0
        positions_for_curve: dict[str, int] = {}
        overlay_orders_by_exec: dict[date, list[dict[str, Any]]] = {}
        for row in overlay_order_rows:
            overlay_orders_by_exec.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)
        for trade_date in trade_dates:
            for row in baseline_orders_by_exec.get(trade_date, []):
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                action = str(row["action"])
                execution_price = _to_float(row["execution_price"])
                rationale = str(row.get("rationale", ""))
                if action == "buy":
                    notional = quantity * execution_price
                    cash_for_curve -= notional + _costs(action="buy", notional=notional)["total_cost"]
                    positions_for_curve[symbol] = positions_for_curve.get(symbol, 0) + quantity
                else:
                    current_qty = positions_for_curve.get(symbol, 0)
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
                    cash_for_curve += notional - _costs(action="sell", notional=notional)["total_cost"]
                    positions_for_curve[symbol] = max(0, current_qty - sell_qty)

            for row in overlay_orders_by_exec.get(trade_date, []):
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                execution_price = _to_float(row["execution_price"])
                notional = quantity * execution_price
                cash_for_curve -= notional + _costs(action="buy", notional=notional)["total_cost"]
                positions_for_curve[symbol] = positions_for_curve.get(symbol, 0) + quantity

            market_value = 0.0
            for symbol, qty in positions_for_curve.items():
                bar = daily_bars.get((symbol, trade_date))
                if bar is None:
                    continue
                market_value += qty * _to_float(bar["close"])
            equity_curve.append(cash_for_curve + market_value)

        baseline_equity_curve = [_to_float(row.get("equity_after_close")) for row in baseline_day_rows]
        summary = {
            "acceptance_posture": "freeze_v115p_cpo_intraday_timing_aware_overlay_replay_v1",
            "candidate_only_overlay": True,
            "overlay_scope": "strict_add_bands_on_already_held_mature_names_only",
            "timing_bucket_used": "intraday_same_session_next_30m_bar_open",
            "strict_overlay_order_count": len(overlay_order_rows),
            "baseline_final_equity": round(baseline_equity_curve[-1], 4),
            "timing_aware_overlay_final_equity": round(equity_curve[-1], 4),
            "final_equity_delta_vs_baseline": round(equity_curve[-1] - baseline_equity_curve[-1], 4),
            "baseline_max_drawdown": _max_drawdown(baseline_equity_curve),
            "timing_aware_overlay_max_drawdown": _max_drawdown(equity_curve),
            "overlay_total_transaction_cost": round(sum(_to_float(row["total_cost"]) for row in overlay_order_rows), 4),
            "recommended_next_posture": "treat_timing_aware_intraday_overlay_as_candidate_execution_semantics_not_as_promoted_law",
        }
        interpretation = [
            "V1.15P replaces the conservative T+1-open execution assumption with a same-session next-30min-bar-open fill, but only for strict signals that V115O proves are already visible intraday.",
            "This remains a narrow held-position overlay and does not open fresh names or override baseline sell-side controls.",
            "The comparison against V114T shows how much of the previous underestimation came from forcing intraday signals into a next-day execution bucket.",
        ]
        return V115PCpoIntradayTimingAwareOverlayReplayReport(
            summary=summary,
            overlay_order_rows=overlay_order_rows,
            interpretation=interpretation,
        )


def write_report(*, reports_dir: Path, report_name: str, result: V115PCpoIntradayTimingAwareOverlayReplayReport) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115PCpoIntradayTimingAwareOverlayReplayAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v115m_payload=json.loads((repo_root / "reports" / "analysis" / "v115m_cpo_intraday_strict_band_overlay_audit_v1.json").read_text(encoding="utf-8")),
        v115o_payload=json.loads((repo_root / "reports" / "analysis" / "v115o_cpo_intraday_strict_band_signal_timing_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115p_cpo_intraday_timing_aware_overlay_replay_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
