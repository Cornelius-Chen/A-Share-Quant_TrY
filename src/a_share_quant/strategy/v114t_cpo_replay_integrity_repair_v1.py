from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from statistics import median
from typing import Any

from a_share_quant.execution.engine import ExecutionEngine
from a_share_quant.execution.models import (
    AccountSnapshot,
    ExecutionIntent,
    PositionSnapshot,
    SymbolMarketState,
)


@dataclass(slots=True)
class V114TCpoReplayIntegrityRepairReport:
    summary: dict[str, Any]
    replay_day_rows: list[dict[str, Any]]
    executed_order_rows: list[dict[str, Any]]
    blocked_intent_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "replay_day_rows": self.replay_day_rows,
            "executed_order_rows": self.executed_order_rows,
            "blocked_intent_rows": self.blocked_intent_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def parse_trade_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def board_from_symbol(symbol: str) -> str:
    if symbol.startswith("688"):
        return "STAR"
    if symbol.startswith(("300", "301")):
        return "ChiNext"
    return "MainBoard"


class V114TCpoReplayIntegrityRepairAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _load_daily_bars(self, path: Path) -> dict[tuple[str, date], dict[str, Any]]:
        result: dict[tuple[str, date], dict[str, Any]] = {}
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                symbol = str(row["symbol"])
                trade_date = parse_trade_date(str(row["trade_date"]))
                result[(symbol, trade_date)] = {
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                    "turnover": float(row["turnover"]),
                    "pre_close": float(row["pre_close"]),
                    "listed_days": int(float(row["listed_days"])),
                    "is_st": str(row["is_st"]).lower() == "true",
                    "is_suspended": str(row["is_suspended"]).lower() == "true",
                }
        return result

    def _average_turnover(
        self,
        daily_bars: dict[tuple[str, date], dict[str, Any]],
        *,
        symbol: str,
        trade_date: date,
        lookback: int,
    ) -> float:
        symbol_rows = sorted(
            ((dt, payload) for (sym, dt), payload in daily_bars.items() if sym == symbol and dt <= trade_date),
            key=lambda item: item[0],
        )
        if not symbol_rows:
            return 0.0
        selected = [payload["turnover"] for _, payload in symbol_rows[-lookback:]]
        return sum(selected) / len(selected)

    def _make_market_state(
        self,
        *,
        symbol: str,
        trade_date: date,
        daily_bars: dict[tuple[str, date], dict[str, Any]],
    ) -> SymbolMarketState | None:
        row = daily_bars.get((symbol, trade_date))
        if row is None:
            return None
        close_price = float(row["close"])
        prev_close = float(row["pre_close"])
        open_price = float(row["open"])
        open_pct = 0.0 if prev_close <= 0 else (open_price / prev_close) - 1.0
        intraday_volatility = 0.0 if close_price <= 0 else max(0.0, (float(row["high"]) - float(row["low"])) / close_price)
        avg_5d = self._average_turnover(daily_bars, symbol=symbol, trade_date=trade_date, lookback=5)
        avg_20d = self._average_turnover(daily_bars, symbol=symbol, trade_date=trade_date, lookback=20)
        market_cap_proxy = max(float(row["turnover"]) * 20.0, 4_000_000_000.0)
        return SymbolMarketState(
            symbol=symbol,
            trade_date=trade_date,
            board=board_from_symbol(symbol),
            last_price=close_price,
            turnover=float(row["turnover"]),
            market_cap=market_cap_proxy,
            adv_5d=max(avg_5d, float(row["turnover"])),
            adv_20d=max(avg_20d, float(row["turnover"])),
            gap_up_pct=max(0.0, open_pct),
            gap_down_pct=max(0.0, -open_pct),
            intraday_volatility=intraday_volatility,
            is_limit_up=False,
            is_limit_down=False,
            is_near_limit_up=False,
            is_near_limit_down=False,
            is_suspended=bool(row["is_suspended"]),
            is_st=bool(row["is_st"]),
            listed_days=int(row["listed_days"]),
            market_cap_reliable=False,
        )

    def _target_notional(self, object_id: str) -> float:
        if object_id == "packaging_process_enabler":
            return 100_000.0
        if object_id == "core_module_leader":
            return 100_000.0
        if object_id == "high_beta_core_module":
            return 80_000.0
        if object_id == "laser_chip_component":
            return 50_000.0
        return 50_000.0

    def _build_board_context(
        self,
        *,
        trade_date: date,
        board_symbols: set[str],
        daily_bars: dict[tuple[str, date], dict[str, Any]],
    ) -> dict[str, Any]:
        rows: list[dict[str, Any]] = []
        for symbol in sorted(board_symbols):
            row = daily_bars.get((symbol, trade_date))
            if row is None:
                continue
            pre_close = float(row["pre_close"])
            day_return = 0.0 if pre_close <= 0 else float(row["close"]) / pre_close - 1.0
            rows.append({"symbol": symbol, "turnover": float(row["turnover"]), "day_return": day_return})
        if not rows:
            return {
                "symbol_count": 0,
                "advancer_count": 0,
                "decliner_count": 0,
                "breadth": 0.0,
                "avg_return": 0.0,
                "median_return": 0.0,
                "top_turnover_symbols": [],
            }
        advancer_count = sum(1 for row in rows if row["day_return"] > 0)
        decliner_count = sum(1 for row in rows if row["day_return"] < 0)
        ordered = sorted(rows, key=lambda item: item["turnover"], reverse=True)
        top_turnover_symbols = [row["symbol"] for row in ordered[:5]]
        top3_turnover = sum(row["turnover"] for row in ordered[:3])
        total_turnover = sum(row["turnover"] for row in ordered)
        return {
            "symbol_count": len(rows),
            "advancer_count": advancer_count,
            "decliner_count": decliner_count,
            "breadth": round((advancer_count - decliner_count) / len(rows), 6),
            "avg_return": round(sum(row["day_return"] for row in rows) / len(rows), 6),
            "median_return": round(float(median(row["day_return"] for row in rows)), 6),
            "top_turnover_symbols": top_turnover_symbols,
            "top3_turnover_ratio": round(0.0 if total_turnover <= 0 else top3_turnover / total_turnover, 6),
        }

    def _trade_costs(self, *, action: str, notional: float) -> dict[str, float]:
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

    def analyze(
        self,
        *,
        v112aa_payload: dict[str, Any],
        v113n_payload: dict[str, Any],
        v113t_payload: dict[str, Any],
        v113u_payload: dict[str, Any],
    ) -> V114TCpoReplayIntegrityRepairReport:
        n_summary = dict(v113n_payload.get("summary", {}))
        u_summary = dict(v113u_payload.get("summary", {}))
        if str(n_summary.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.14T expects V1.13N real episode population first.")
        if str(u_summary.get("acceptance_posture")) != "freeze_v113u_cpo_execution_main_feed_readiness_audit_v1":
            raise ValueError("V1.14T expects V1.13U execution main feed readiness audit first.")
        if not bool(u_summary.get("execution_main_feed_ready_now", False)):
            raise ValueError("V1.14T requires execution main feed readiness to be true.")

        raw_daily_path = self.repo_root / str(dict(v113t_payload.get("summary", {}))["output_csv"])
        risk_limits_path = self.repo_root / "PROJECT_LIMITATION" / "risk_limits.yaml"
        daily_bars = self._load_daily_bars(raw_daily_path)
        engine = ExecutionEngine(risk_limits_path=risk_limits_path)

        cohort_rows = list(v112aa_payload.get("object_role_time_rows", []))
        board_symbols = {str(row["symbol"]) for row in cohort_rows}
        episode_rows = list(v113n_payload.get("internal_point_rows", []))
        episode_by_date: dict[date, list[dict[str, Any]]] = {}
        for row in episode_rows:
            trade_date = parse_trade_date(str(row["trade_date"]))
            episode_by_date.setdefault(trade_date, []).append(row)

        min_episode_date = min(parse_trade_date(str(row["trade_date"])) for row in episode_rows)
        max_episode_date = max(parse_trade_date(str(row["trade_date"])) for row in episode_rows)
        trade_dates = sorted({trade_date for (_, trade_date) in daily_bars if min_episode_date <= trade_date <= max_episode_date})
        next_trade_date_map = {
            trade_dates[idx]: trade_dates[idx + 1]
            for idx in range(len(trade_dates) - 1)
        }

        symbol_map = {
            "packaging_process_enabler": "300757",
            "core_module_leader": "300308",
            "high_beta_core_module": "300502",
            "laser_chip_component": "688498",
        }

        account_cash = 1_000_000.0
        positions_qty: dict[str, int] = {}
        positions_sellable_qty: dict[str, int] = {}
        positions_last_buy_date: dict[str, date | None] = {}
        equity_peak = 1_000_000.0
        previous_equity = 1_000_000.0
        pending_orders: dict[date, list[dict[str, Any]]] = {}
        executed_order_rows: list[dict[str, Any]] = []
        blocked_intent_rows: list[dict[str, Any]] = []
        replay_day_rows: list[dict[str, Any]] = []

        for trade_date in trade_dates:
            for symbol, qty in list(positions_qty.items()):
                last_buy_date = positions_last_buy_date.get(symbol)
                if qty <= 0:
                    positions_sellable_qty[symbol] = 0
                elif last_buy_date is None or last_buy_date < trade_date:
                    positions_sellable_qty[symbol] = qty

            executed_today_turnover = 0.0
            for pending in pending_orders.pop(trade_date, []):
                row = daily_bars.get((pending["symbol"], trade_date))
                if row is None or bool(row["is_suspended"]):
                    blocked_intent_rows.append(
                        {
                            "signal_trade_date": str(pending["signal_trade_date"]),
                            "execution_trade_date": str(trade_date),
                            "symbol": pending["symbol"],
                            "action": pending["action"],
                            "requested_quantity": pending["quantity"],
                            "source": pending["source"],
                            "reason": "next_day_execution_row_missing_or_suspended",
                        }
                    )
                    continue

                execution_price = float(row["open"])
                quantity = int(pending["quantity"])
                if pending["action"] == "buy":
                    affordable_qty = int(account_cash // (execution_price * 1.0018))
                    affordable_qty = (affordable_qty // 100) * 100
                    quantity = min(quantity, max(0, affordable_qty))
                else:
                    quantity = min(quantity, positions_sellable_qty.get(pending["symbol"], positions_qty.get(pending["symbol"], 0)))
                if quantity <= 0:
                    blocked_intent_rows.append(
                        {
                            "signal_trade_date": str(pending["signal_trade_date"]),
                            "execution_trade_date": str(trade_date),
                            "symbol": pending["symbol"],
                            "action": pending["action"],
                            "requested_quantity": pending["quantity"],
                            "source": pending["source"],
                            "reason": "quantity_reduced_to_zero_at_execution",
                        }
                    )
                    continue

                notional = round(quantity * execution_price, 4)
                cost = self._trade_costs(action=pending["action"], notional=notional)
                if pending["action"] == "buy":
                    account_cash -= notional + cost["total_cost"]
                    positions_qty[pending["symbol"]] = positions_qty.get(pending["symbol"], 0) + quantity
                    positions_last_buy_date[pending["symbol"]] = trade_date
                else:
                    current_qty = positions_qty.get(pending["symbol"], 0)
                    current_sellable = positions_sellable_qty.get(pending["symbol"], current_qty)
                    positions_qty[pending["symbol"]] = max(0, current_qty - quantity)
                    positions_sellable_qty[pending["symbol"]] = max(0, current_sellable - quantity)
                    if positions_qty[pending["symbol"]] == 0:
                        positions_last_buy_date[pending["symbol"]] = None
                    account_cash += notional - cost["total_cost"]
                executed_today_turnover += notional
                executed_order_rows.append(
                    {
                        "signal_trade_date": str(pending["signal_trade_date"]),
                        "execution_trade_date": str(trade_date),
                        "symbol": pending["symbol"],
                        "action": pending["action"],
                        "quantity": quantity,
                        "signal_reference_price": pending["signal_reference_price"],
                        "execution_price": execution_price,
                        "notional": notional,
                        "commission": cost["commission"],
                        "stamp_tax": cost["stamp_tax"],
                        "slippage": cost["slippage"],
                        "total_cost": cost["total_cost"],
                        "posture": pending["posture"],
                        "source": pending["source"],
                        "rationale": pending["rationale"],
                    }
                )

            market_by_symbol: dict[str, SymbolMarketState] = {}
            for symbol in board_symbols | set(positions_qty.keys()):
                market_state = self._make_market_state(symbol=symbol, trade_date=trade_date, daily_bars=daily_bars)
                if market_state is not None:
                    market_by_symbol[symbol] = market_state

            market_value = 0.0
            positions_by_symbol: dict[str, PositionSnapshot] = {}
            for symbol, qty in positions_qty.items():
                market_state = market_by_symbol.get(symbol)
                if market_state is None:
                    continue
                value = qty * market_state.last_price
                market_value += value
                if previous_equity > 0:
                    positions_by_symbol[symbol] = PositionSnapshot(
                        symbol=symbol,
                        quantity=qty,
                        market_value=value,
                        strategy_weight=value / previous_equity,
                        account_weight=value / previous_equity,
                        add_count_today=0,
                        order_count_today=0,
                        sellable_quantity=positions_sellable_qty.get(symbol, qty),
                        last_buy_trade_date=positions_last_buy_date.get(symbol),
                    )

            equity = account_cash + market_value
            equity_peak = max(equity_peak, equity)
            daily_pnl_pct = 0.0 if previous_equity <= 0 else equity / previous_equity - 1.0
            daily_loss_pct = abs(min(0.0, daily_pnl_pct))
            strategy_drawdown_pct = 0.0 if equity_peak <= 0 else max(0.0, 1.0 - equity / equity_peak)

            account = AccountSnapshot(
                trade_date=trade_date,
                account_id="cpo_paper_1m_full_board_repaired",
                cash=account_cash,
                equity=equity,
                gross_exposure=0.0 if equity <= 0 else market_value / equity,
                net_exposure=0.0 if equity <= 0 else market_value / equity,
                daily_turnover=executed_today_turnover,
                daily_loss_pct=daily_loss_pct,
                strategy_drawdown_pct=strategy_drawdown_pct,
                account_drawdown_pct=strategy_drawdown_pct,
                open_order_count=0,
                open_position_count=len([qty for qty in positions_qty.values() if qty > 0]),
            )

            intents: list[ExecutionIntent] = []
            day_episode_rows = episode_by_date.get(trade_date, [])
            for row in day_episode_rows:
                object_id = str(row["object_id"])
                symbol = symbol_map.get(object_id)
                if symbol is None:
                    continue
                control_label = str(row["control_label_assistant"])
                confidence_tier = str(row["assistant_confidence_tier"])
                qty_held = positions_qty.get(symbol, 0)
                market_state = market_by_symbol.get(symbol)
                if market_state is None:
                    blocked_intent_rows.append(
                        {
                            "signal_trade_date": str(trade_date),
                            "execution_trade_date": None,
                            "symbol": symbol,
                            "action": "buy",
                            "requested_quantity": 0,
                            "source": f"{object_id}:{control_label}",
                            "reason": "market_state_missing_in_execution_main_feed",
                        }
                    )
                    continue
                target_notional = self._target_notional(object_id)
                lot_qty = int((target_notional / market_state.last_price) // 100) * 100
                if lot_qty <= 0:
                    continue
                if control_label in {"eligibility", "admission_extension"}:
                    if qty_held <= 0:
                        intents.append(
                            ExecutionIntent(
                                trade_date=trade_date,
                                symbol=symbol,
                                action="buy",
                                quantity=lot_qty,
                                strategy_id="cpo_full_board_repaired",
                                source=f"{object_id}:{control_label}",
                                rationale="open_from_board_state_episode",
                                tags=(object_id, control_label, confidence_tier, "open"),
                            )
                        )
                    elif qty_held < lot_qty:
                        add_qty = max(0, ((lot_qty - qty_held) // 100) * 100)
                        if add_qty > 0:
                            intents.append(
                                ExecutionIntent(
                                    trade_date=trade_date,
                                    symbol=symbol,
                                    action="buy",
                                    quantity=add_qty,
                                    strategy_id="cpo_full_board_repaired",
                                    source=f"{object_id}:{control_label}",
                                    rationale="add_to_target_from_board_state_episode",
                                    tags=(object_id, control_label, confidence_tier, "add"),
                                )
                            )
                elif control_label == "de_risk" and qty_held > 0:
                    reduce_qty = max(100, (qty_held // 2 // 100) * 100)
                    reduce_qty = min(reduce_qty, qty_held)
                    intents.append(
                        ExecutionIntent(
                            trade_date=trade_date,
                            symbol=symbol,
                            action="sell",
                            quantity=reduce_qty,
                            strategy_id="cpo_full_board_repaired",
                            source=f"{object_id}:{control_label}",
                            rationale="reduce_from_board_state_episode",
                            tags=(object_id, control_label, confidence_tier, "reduce"),
                        )
                    )
                elif control_label == "holding_veto" and qty_held > 0:
                    intents.append(
                        ExecutionIntent(
                            trade_date=trade_date,
                            symbol=symbol,
                            action="sell",
                            quantity=qty_held,
                            strategy_id="cpo_full_board_repaired",
                            source=f"{object_id}:{control_label}",
                            rationale="close_from_holding_veto",
                            tags=(object_id, control_label, confidence_tier, "close"),
                        )
                    )

            plan = engine.build_plan(
                intents=intents,
                account=account,
                positions_by_symbol=positions_by_symbol,
                market_by_symbol=market_by_symbol,
            )

            next_trade_date = next_trade_date_map.get(trade_date)
            for order in plan.orders:
                if next_trade_date is None:
                    blocked_intent_rows.append(
                        {
                            "signal_trade_date": str(trade_date),
                            "execution_trade_date": None,
                            "symbol": order.symbol,
                            "action": order.action,
                            "requested_quantity": order.quantity,
                            "source": order.source,
                            "reason": "no_next_trade_day_for_execution",
                        }
                    )
                    continue
                pending_orders.setdefault(next_trade_date, []).append(
                    {
                        "signal_trade_date": trade_date,
                        "symbol": order.symbol,
                        "action": order.action,
                        "quantity": order.quantity,
                        "signal_reference_price": order.reference_price,
                        "posture": order.posture,
                        "source": order.source,
                        "rationale": order.rationale,
                    }
                )

            for blocked in plan.blocked_intents:
                blocked_intent_rows.append(
                    {
                        "signal_trade_date": str(trade_date),
                        "execution_trade_date": None,
                        "symbol": blocked.symbol,
                        "action": blocked.action,
                        "requested_quantity": blocked.quantity,
                        "source": blocked.source,
                        "reason": "execution_engine_block",
                    }
                )

            replay_day_rows.append(
                {
                    "trade_date": str(trade_date),
                    "episode_count": len(day_episode_rows),
                    "intent_count": len(intents),
                    "planned_order_count": len(plan.orders),
                    "blocked_intent_count": len(plan.blocked_intents),
                    "executed_today_order_count": len([row for row in executed_order_rows if row["execution_trade_date"] == str(trade_date)]),
                    "cash_after_close": round(account_cash, 4),
                    "equity_after_close": round(equity, 4),
                    "gross_exposure_after_close": round(0.0 if equity <= 0 else market_value / equity, 6),
                    "day_turnover_notional": round(executed_today_turnover, 4),
                    "board_context": self._build_board_context(trade_date=trade_date, board_symbols=board_symbols, daily_bars=daily_bars),
                }
            )
            previous_equity = equity

        total_cost = round(sum(float(row["total_cost"]) for row in executed_order_rows), 4)
        summary = {
            "acceptance_posture": "freeze_v114t_cpo_replay_integrity_repair_v1",
            "board_name": "CPO",
            "initial_capital": 1_000_000.0,
            "execution_timing": "signal_on_t_close_execute_on_t_plus_1_open",
            "margin_enabled": False,
            "shorting_enabled": False,
            "t_plus_one_enabled": True,
            "cost_model": {
                "commission_rate": 0.0003,
                "min_commission": 5.0,
                "sell_stamp_tax_rate": 0.001,
                "slippage_bps": 5.0,
            },
            "execution_main_feed_symbol_count": len(board_symbols),
            "replay_trade_day_count": len(replay_day_rows),
            "executed_order_count": len(executed_order_rows),
            "blocked_intent_count": len(blocked_intent_rows),
            "total_transaction_cost": total_cost,
            "final_cash": round(account_cash, 4),
            "final_equity": round(previous_equity, 4),
            "recommended_next_posture": "rerun_under_exposure_and_sizing_reviews_on_integrity_repaired_replay_before_any_new_promotion",
        }
        interpretation = [
            "V1.14T repairs the most serious replay integrity flaws by moving execution to next-day open and charging explicit transaction costs.",
            "This is still a research replay, but it is materially less optimistic than the original same-day close execution loop.",
            "Any later sizing, overlay, or confirmation judgement should migrate to this repaired replay surface before further promotion.",
        ]
        return V114TCpoReplayIntegrityRepairReport(
            summary=summary,
            replay_day_rows=replay_day_rows,
            executed_order_rows=executed_order_rows,
            blocked_intent_rows=blocked_intent_rows,
            interpretation=interpretation,
        )


def write_v114t_cpo_replay_integrity_repair_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114TCpoReplayIntegrityRepairReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V114TCpoReplayIntegrityRepairAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v112aa_payload=load_json_report(repo_root / "reports" / "analysis" / "v112aa_cpo_bounded_cohort_map_v1.json"),
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113t_payload=load_json_report(repo_root / "reports" / "analysis" / "v113t_cpo_execution_main_feed_build_v1.json"),
        v113u_payload=load_json_report(repo_root / "reports" / "analysis" / "v113u_cpo_execution_main_feed_readiness_audit_v1.json"),
    )
    output_path = write_v114t_cpo_replay_integrity_repair_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v114t_cpo_replay_integrity_repair_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
