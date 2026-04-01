from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


def parse_trade_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _costs(*, action: str, notional: float) -> dict[str, float]:
    commission_rate = 0.0003
    min_commission = 5.0
    stamp_tax_rate = 0.001 if action == "sell" else 0.0
    slippage_bps = 5.0
    commission = max(min_commission, notional * commission_rate) if notional > 0 else 0.0
    stamp_tax = notional * stamp_tax_rate
    slippage = notional * (slippage_bps / 10000.0)
    total_cost = commission + stamp_tax + slippage
    return {
        "commission": round(commission, 4),
        "stamp_tax": round(stamp_tax, 4),
        "slippage": round(slippage, 4),
        "total_cost": round(total_cost, 4),
    }


def _max_drawdown(equity_curve: list[float]) -> float:
    peak = 0.0
    max_dd = 0.0
    for equity in equity_curve:
        peak = max(peak, equity)
        if peak > 0:
            max_dd = max(max_dd, 1.0 - equity / peak)
    return round(max_dd, 6)


def _load_daily_bars(path: Path) -> dict[tuple[str, date], dict[str, Any]]:
    rows: dict[tuple[str, date], dict[str, Any]] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            trade_date = parse_trade_date(str(row["trade_date"]))
            symbol = str(row["symbol"])
            rows[(symbol, trade_date)] = {
                "open": _to_float(row["open"]),
                "close": _to_float(row["close"]),
                "high": _to_float(row["high"]),
                "low": _to_float(row["low"]),
                "turnover": _to_float(row["turnover"]),
                "pre_close": _to_float(row["pre_close"]),
            }
    return rows


def _load_overlay_rows(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class OverlaySignal:
    signal_trade_date: date
    symbol: str
    state_band: str
    expectancy_proxy_3d: float
    max_adverse_return_3d: float


@dataclass(slots=True)
class V115NCpoIntradayStrictBandHeldPositionOverlayReplayReport:
    summary: dict[str, Any]
    overlay_order_rows: list[dict[str, Any]]
    replay_day_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "overlay_order_rows": self.overlay_order_rows,
            "replay_day_rows": self.replay_day_rows,
            "interpretation": self.interpretation,
        }


class V115NCpoIntradayStrictBandHeldPositionOverlayReplayAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    @staticmethod
    def _baseline_sell_fraction(executed_orders: list[dict[str, Any]]) -> dict[tuple[date, str], float]:
        positions: dict[str, int] = {}
        fractions: dict[tuple[date, str], float] = {}
        ordered = sorted(
            executed_orders,
            key=lambda row: (parse_trade_date(str(row["execution_trade_date"])), str(row["symbol"]), str(row["action"])),
        )
        for row in ordered:
            symbol = str(row["symbol"])
            exec_date = parse_trade_date(str(row["execution_trade_date"]))
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

    @staticmethod
    def _end_of_day_positions(
        executed_orders: list[dict[str, Any]],
        *,
        trade_dates: list[date],
    ) -> dict[tuple[date, str], int]:
        positions: dict[str, int] = {}
        by_day: dict[tuple[date, str], int] = {}
        ordered = sorted(
            executed_orders,
            key=lambda row: (parse_trade_date(str(row["execution_trade_date"])), str(row["symbol"]), str(row["action"])),
        )
        rows_by_date: dict[date, list[dict[str, Any]]] = {}
        for row in ordered:
            rows_by_date.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)
        known_symbols = sorted({str(row["symbol"]) for row in executed_orders})
        for trade_date in trade_dates:
            for row in rows_by_date.get(trade_date, []):
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                if str(row["action"]) == "buy":
                    positions[symbol] = positions.get(symbol, 0) + quantity
                else:
                    positions[symbol] = max(0, positions.get(symbol, 0) - quantity)
            for symbol in known_symbols:
                qty = positions.get(symbol, 0)
                by_day[(trade_date, symbol)] = qty
        return by_day

    def analyze(
        self,
        *,
        v113t_payload: dict[str, Any],
        v114t_payload: dict[str, Any],
        v115m_payload: dict[str, Any],
    ) -> V115NCpoIntradayStrictBandHeldPositionOverlayReplayReport:
        if str(v114t_payload.get("summary", {}).get("acceptance_posture")) != "freeze_v114t_cpo_replay_integrity_repair_v1":
            raise ValueError("V115N expects repaired replay baseline from V114T.")
        if str(v115m_payload.get("summary", {}).get("acceptance_posture")) != "freeze_v115m_cpo_intraday_strict_band_overlay_audit_v1":
            raise ValueError("V115N expects V115M strict overlay audit first.")

        daily_path = self.repo_root / str(v113t_payload["summary"]["output_csv"])
        daily_bars = _load_daily_bars(daily_path)

        baseline_executed_orders = list(v114t_payload.get("executed_order_rows", []))
        baseline_day_rows = list(v114t_payload.get("replay_day_rows", []))
        baseline_day_map = {
            parse_trade_date(str(row["trade_date"])): row
            for row in baseline_day_rows
        }
        trade_dates = sorted(baseline_day_map.keys())
        next_trade_date_map = {
            trade_dates[idx]: trade_dates[idx + 1]
            for idx in range(len(trade_dates) - 1)
        }
        baseline_positions_eod = self._end_of_day_positions(baseline_executed_orders, trade_dates=trade_dates)
        baseline_sell_fraction = self._baseline_sell_fraction(baseline_executed_orders)

        miss_days = {
            parse_trade_date(str(row["trade_date"])): row
            for row in list(v115m_payload.get("miss_day_uplift_rows", []))
        }
        strict_hit_rows = [
            OverlaySignal(
                signal_trade_date=parse_trade_date(str(row["signal_trade_date"])),
                symbol=str(row["symbol"]),
                state_band=str(row["state_band"]),
                expectancy_proxy_3d=_to_float(row["expectancy_proxy_3d"]),
                max_adverse_return_3d=_to_float(row["max_adverse_return_3d"]),
            )
            for row in list(v115m_payload.get("strict_overlay_hit_rows", []))
        ]

        overlay_fill_fraction = 0.5
        per_symbol_position_add_cap_ratio = 0.5
        max_extra_notional_per_symbol = 100_000.0

        overlay_schedule: dict[date, list[dict[str, Any]]] = {}
        overlay_order_rows: list[dict[str, Any]] = []

        strict_rows_by_signal: dict[date, list[OverlaySignal]] = {}
        for row in strict_hit_rows:
            strict_rows_by_signal.setdefault(row.signal_trade_date, []).append(row)

        for signal_trade_date, miss_row in miss_days.items():
            hit_rows = strict_rows_by_signal.get(signal_trade_date, [])
            if not hit_rows:
                continue
            baseline_day = baseline_day_map.get(signal_trade_date)
            if baseline_day is None:
                continue
            signal_equity = _to_float(baseline_day.get("equity_after_close"))
            gap_to_floor = _to_float(miss_row.get("gross_exposure_gap_to_floor"))
            if signal_equity <= 0 or gap_to_floor <= 0:
                continue
            valid_hits: list[tuple[OverlaySignal, int, float]] = []
            for hit in hit_rows:
                held_qty = baseline_positions_eod.get((signal_trade_date, hit.symbol), 0)
                if held_qty <= 0:
                    continue
                close_row = daily_bars.get((hit.symbol, signal_trade_date))
                if close_row is None:
                    continue
                held_value = held_qty * _to_float(close_row["close"])
                valid_hits.append((hit, held_qty, held_value))
            if not valid_hits:
                continue
            execution_trade_date = next_trade_date_map.get(signal_trade_date)
            if execution_trade_date is None:
                continue
            gross_pool = signal_equity * gap_to_floor * overlay_fill_fraction
            per_hit_pool = gross_pool / len(valid_hits)
            for hit, held_qty, held_value in valid_hits:
                capped_notional = min(per_hit_pool, held_value * per_symbol_position_add_cap_ratio, max_extra_notional_per_symbol)
                exec_row = daily_bars.get((hit.symbol, execution_trade_date))
                if exec_row is None:
                    continue
                execution_price = _to_float(exec_row["open"])
                quantity = int((capped_notional / execution_price) // 100) * 100 if execution_price > 0 else 0
                if quantity <= 0:
                    continue
                overlay_payload = {
                    "signal_trade_date": signal_trade_date,
                    "execution_trade_date": execution_trade_date,
                    "symbol": hit.symbol,
                    "state_band": hit.state_band,
                    "expectancy_proxy_3d": hit.expectancy_proxy_3d,
                    "max_adverse_return_3d": hit.max_adverse_return_3d,
                    "requested_quantity": quantity,
                    "capped_notional": round(capped_notional, 4),
                    "execution_price": execution_price,
                    "signal_equity": round(signal_equity, 4),
                    "gross_exposure_gap_to_floor": round(gap_to_floor, 6),
                }
                overlay_schedule.setdefault(execution_trade_date, []).append(overlay_payload)

        baseline_orders_by_exec: dict[date, list[dict[str, Any]]] = {}
        for row in baseline_executed_orders:
            baseline_orders_by_exec.setdefault(parse_trade_date(str(row["execution_trade_date"])), []).append(row)

        cash = 1_000_000.0
        positions: dict[str, int] = {}
        equity_curve: list[float] = []
        replay_day_rows: list[dict[str, Any]] = []

        for trade_date in trade_dates:
            for row in baseline_orders_by_exec.get(trade_date, []):
                symbol = str(row["symbol"])
                quantity = int(row["quantity"])
                action = str(row["action"])
                execution_price = _to_float(row["execution_price"])
                rationale = str(row.get("rationale", ""))
                if action == "buy":
                    notional = quantity * execution_price
                    cost = _costs(action="buy", notional=notional)
                    cash -= notional + cost["total_cost"]
                    positions[symbol] = positions.get(symbol, 0) + quantity
                    continue
                current_qty = positions.get(symbol, 0)
                if current_qty <= 0:
                    continue
                if rationale == "close_from_holding_veto":
                    sell_qty = current_qty
                elif rationale == "reduce_from_board_state_episode":
                    fraction = baseline_sell_fraction.get((trade_date, symbol), 0.0)
                    sell_qty = int((current_qty * fraction) // 100) * 100
                    if sell_qty <= 0 and current_qty > 0:
                        sell_qty = min(current_qty, 100 if current_qty >= 100 else current_qty)
                else:
                    sell_qty = min(current_qty, quantity)
                sell_qty = min(current_qty, sell_qty)
                if sell_qty <= 0:
                    continue
                notional = sell_qty * execution_price
                cost = _costs(action="sell", notional=notional)
                cash += notional - cost["total_cost"]
                positions[symbol] = max(0, current_qty - sell_qty)

            for overlay in overlay_schedule.get(trade_date, []):
                symbol = str(overlay["symbol"])
                execution_price = _to_float(overlay["execution_price"])
                quantity = int(overlay["requested_quantity"])
                affordable_qty = int(cash // (execution_price * 1.0018)) if execution_price > 0 else 0
                affordable_qty = (affordable_qty // 100) * 100
                quantity = min(quantity, max(0, affordable_qty))
                if quantity <= 0:
                    continue
                notional = quantity * execution_price
                cost = _costs(action="buy", notional=notional)
                cash -= notional + cost["total_cost"]
                positions[symbol] = positions.get(symbol, 0) + quantity
                overlay_order_rows.append(
                    {
                        "signal_trade_date": str(overlay["signal_trade_date"]),
                        "execution_trade_date": str(trade_date),
                        "symbol": symbol,
                        "action": "buy",
                        "quantity": quantity,
                        "execution_price": execution_price,
                        "notional": round(notional, 4),
                        "commission": cost["commission"],
                        "stamp_tax": cost["stamp_tax"],
                        "slippage": cost["slippage"],
                        "total_cost": cost["total_cost"],
                        "state_band": str(overlay["state_band"]),
                        "expectancy_proxy_3d": round(_to_float(overlay["expectancy_proxy_3d"]), 6),
                        "max_adverse_return_3d": round(_to_float(overlay["max_adverse_return_3d"]), 6),
                        "overlay_posture": "strict_held_position_add_only",
                    }
                )

            market_value = 0.0
            for symbol, qty in positions.items():
                row = daily_bars.get((symbol, trade_date))
                if row is None:
                    continue
                market_value += qty * _to_float(row["close"])
            equity = cash + market_value
            equity_curve.append(equity)
            baseline_row = baseline_day_map[trade_date]
            replay_day_rows.append(
                {
                    "trade_date": str(trade_date),
                    "baseline_equity_after_close": round(_to_float(baseline_row.get("equity_after_close")), 4),
                    "overlay_equity_after_close": round(equity, 4),
                    "equity_delta_vs_baseline": round(equity - _to_float(baseline_row.get("equity_after_close")), 4),
                    "baseline_gross_exposure_after_close": round(_to_float(baseline_row.get("gross_exposure_after_close")), 6),
                    "overlay_gross_exposure_after_close": round(0.0 if equity <= 0 else market_value / equity, 6),
                    "overlay_order_count_today": len([row for row in overlay_order_rows if row["execution_trade_date"] == str(trade_date)]),
                }
            )

        baseline_equity_curve = [_to_float(row.get("equity_after_close")) for row in baseline_day_rows]
        final_overlay_equity = equity_curve[-1] if equity_curve else 1_000_000.0
        final_baseline_equity = baseline_equity_curve[-1] if baseline_equity_curve else 1_000_000.0

        summary = {
            "acceptance_posture": "freeze_v115n_cpo_intraday_strict_band_held_position_overlay_replay_v1",
            "candidate_only_overlay": True,
            "overlay_scope": "strict_add_bands_on_already_held_mature_names_only",
            "overlay_fill_fraction": overlay_fill_fraction,
            "per_symbol_position_add_cap_ratio": per_symbol_position_add_cap_ratio,
            "max_extra_notional_per_symbol": max_extra_notional_per_symbol,
            "strict_miss_day_count": len(miss_days),
            "strict_overlay_order_count": len(overlay_order_rows),
            "baseline_final_equity": round(final_baseline_equity, 4),
            "overlay_final_equity": round(final_overlay_equity, 4),
            "final_equity_delta": round(final_overlay_equity - final_baseline_equity, 4),
            "baseline_max_drawdown": _max_drawdown(baseline_equity_curve),
            "overlay_max_drawdown": _max_drawdown(equity_curve),
            "overlay_total_transaction_cost": round(sum(_to_float(row["total_cost"]) for row in overlay_order_rows), 4),
            "recommended_next_posture": "strict_intraday_overlay_can_only_remain_candidate_until_incremental_value_is_revalidated_on_repaired_replay",
        }
        interpretation = [
            "V1.15N binds strict intraday add bands into the repaired replay only as held-position overlays on already-held mature names.",
            "This replay does not let intraday bands open fresh symbols and does not let them override baseline sell-side hard controls.",
            "The result should be read as a narrow candidate overlay audit, not as promotion of a new admission or generic intraday add law.",
        ]
        return V115NCpoIntradayStrictBandHeldPositionOverlayReplayReport(
            summary=summary,
            overlay_order_rows=overlay_order_rows,
            replay_day_rows=replay_day_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115NCpoIntradayStrictBandHeldPositionOverlayReplayReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V115NCpoIntradayStrictBandHeldPositionOverlayReplayAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113t_payload=json.loads((repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json").read_text(encoding="utf-8")),
        v114t_payload=json.loads((repo_root / "reports" / "analysis" / "v114t_cpo_replay_integrity_repair_v1.json").read_text(encoding="utf-8")),
        v115m_payload=json.loads((repo_root / "reports" / "analysis" / "v115m_cpo_intraday_strict_band_overlay_audit_v1.json").read_text(encoding="utf-8")),
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115n_cpo_intraday_strict_band_held_position_overlay_replay_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
