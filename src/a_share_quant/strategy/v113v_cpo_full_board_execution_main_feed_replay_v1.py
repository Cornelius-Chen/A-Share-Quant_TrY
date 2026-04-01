from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
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
class V113VCPOFullBoardExecutionMainFeedReplayReport:
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


def action_mode_from_tags(tags: tuple[str, ...]) -> str:
    for candidate in ("open", "add", "reduce", "close", "flat"):
        if candidate in tags:
            return candidate
    return "unknown"


class V113VCPOFullBoardExecutionMainFeedReplayAnalyzer:
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

    def _load_index_bars(self, path: Path, symbols: set[str]) -> dict[tuple[str, date], dict[str, Any]]:
        result: dict[tuple[str, date], dict[str, Any]] = {}
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                symbol = str(row["symbol"])
                if symbol not in symbols:
                    continue
                trade_date = parse_trade_date(str(row["trade_date"]))
                result[(symbol, trade_date)] = {
                    "close": float(row["close"]),
                    "pre_close": float(row["pre_close"]),
                    "turnover": float(row["turnover"]),
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
        gap_up = 0.0
        gap_down = 0.0
        if prev_close > 0:
            open_pct = (open_price / prev_close) - 1.0
            gap_up = max(0.0, open_pct)
            gap_down = max(0.0, -open_pct)
        intraday_volatility = 0.0
        if close_price > 0:
            intraday_volatility = max(0.0, (float(row["high"]) - float(row["low"])) / close_price)
        avg_5d = self._average_turnover(daily_bars, symbol=symbol, trade_date=trade_date, lookback=5)
        avg_20d = self._average_turnover(daily_bars, symbol=symbol, trade_date=trade_date, lookback=20)
        market_cap = max(float(row["turnover"]) * 20.0, 4_000_000_000.0)
        return SymbolMarketState(
            symbol=symbol,
            trade_date=trade_date,
            board=board_from_symbol(symbol),
            last_price=close_price,
            turnover=float(row["turnover"]),
            market_cap=market_cap,
            adv_5d=max(avg_5d, float(row["turnover"])),
            adv_20d=max(avg_20d, float(row["turnover"])),
            gap_up_pct=gap_up,
            gap_down_pct=gap_down,
            intraday_volatility=intraday_volatility,
            is_limit_up=False,
            is_limit_down=False,
            is_near_limit_up=False,
            is_near_limit_down=False,
            is_suspended=bool(row["is_suspended"]),
            is_st=bool(row["is_st"]),
            listed_days=int(row["listed_days"]),
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
            rows.append(
                {
                    "symbol": symbol,
                    "close": float(row["close"]),
                    "turnover": float(row["turnover"]),
                    "day_return": day_return,
                }
            )
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
        ordered_by_turnover = sorted(rows, key=lambda item: item["turnover"], reverse=True)
        top_turnover_symbols = [row["symbol"] for row in ordered_by_turnover[:5]]
        top3_turnover = sum(row["turnover"] for row in ordered_by_turnover[:3])
        total_turnover = sum(row["turnover"] for row in ordered_by_turnover)
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

    def analyze(
        self,
        *,
        v112aa_payload: dict[str, Any],
        v113n_payload: dict[str, Any],
        v113t_payload: dict[str, Any],
        v113u_payload: dict[str, Any],
    ) -> V113VCPOFullBoardExecutionMainFeedReplayReport:
        n_summary = dict(v113n_payload.get("summary", {}))
        u_summary = dict(v113u_payload.get("summary", {}))
        if str(n_summary.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.13V expects V1.13N real episode population first.")
        if str(u_summary.get("acceptance_posture")) != "freeze_v113u_cpo_execution_main_feed_readiness_audit_v1":
            raise ValueError("V1.13V expects V1.13U execution main feed readiness audit first.")
        if not bool(u_summary.get("execution_main_feed_ready_now", False)):
            raise ValueError("V1.13V requires execution main feed readiness to be true.")

        raw_daily_path = self.repo_root / str(dict(v113t_payload.get("summary", {}))["output_csv"])
        index_path = self.repo_root / "data" / "raw" / "index_daily_bars" / "akshare_index_daily_bars_market_research_v1.csv"
        risk_limits_path = self.repo_root / "PROJECT_LIMITATION" / "risk_limits.yaml"

        daily_bars = self._load_daily_bars(raw_daily_path)
        index_bars = self._load_index_bars(index_path, {"000001", "399006", "000688"})
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
        trade_dates = sorted(
            {
                trade_date
                for (_, trade_date) in daily_bars
                if min_episode_date <= trade_date <= max_episode_date
            }
        )

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
        executed_order_rows: list[dict[str, Any]] = []
        blocked_intent_rows: list[dict[str, Any]] = []
        replay_day_rows: list[dict[str, Any]] = []
        supported_action_modes = ["open", "add", "reduce", "close", "flat"]

        for trade_date in trade_dates:
            for symbol, qty in list(positions_qty.items()):
                last_buy_date = positions_last_buy_date.get(symbol)
                if qty <= 0:
                    positions_sellable_qty[symbol] = 0
                elif last_buy_date is None or last_buy_date < trade_date:
                    positions_sellable_qty[symbol] = qty

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
                account_id="cpo_paper_1m_full_board",
                cash=account_cash,
                equity=equity,
                gross_exposure=0.0 if equity <= 0 else market_value / equity,
                net_exposure=0.0 if equity <= 0 else market_value / equity,
                daily_turnover=0.0,
                daily_loss_pct=daily_loss_pct,
                strategy_drawdown_pct=strategy_drawdown_pct,
                account_drawdown_pct=strategy_drawdown_pct,
                open_order_count=0,
                open_position_count=len([qty for qty in positions_qty.values() if qty > 0]),
            )

            day_episode_rows = episode_by_date.get(trade_date, [])
            intents: list[ExecutionIntent] = []
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
                            "trade_date": str(trade_date),
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
                                strategy_id="cpo_full_board_replay",
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
                                    strategy_id="cpo_full_board_replay",
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
                            strategy_id="cpo_full_board_replay",
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
                            strategy_id="cpo_full_board_replay",
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

            day_turnover = 0.0
            for order in plan.orders:
                if order.action == "buy":
                    positions_qty[order.symbol] = positions_qty.get(order.symbol, 0) + order.quantity
                    positions_sellable_qty[order.symbol] = positions_sellable_qty.get(order.symbol, 0)
                    positions_last_buy_date[order.symbol] = trade_date
                    account_cash -= order.notional
                elif order.action == "sell":
                    current_qty = positions_qty.get(order.symbol, 0)
                    current_sellable = positions_sellable_qty.get(order.symbol, current_qty)
                    positions_qty[order.symbol] = max(0, current_qty - order.quantity)
                    positions_sellable_qty[order.symbol] = max(0, current_sellable - order.quantity)
                    if positions_qty[order.symbol] == 0:
                        positions_last_buy_date[order.symbol] = None
                    account_cash += order.notional
                day_turnover += order.notional
                executed_order_rows.append(
                    {
                        "trade_date": str(order.trade_date),
                        "symbol": order.symbol,
                        "action": order.action,
                        "quantity": order.quantity,
                        "reference_price": order.reference_price,
                        "notional": order.notional,
                        "posture": order.posture,
                        "source": order.source,
                        "rationale": order.rationale,
                        "action_mode": action_mode_from_tags(
                            next(
                                (
                                    intent.tags
                                    for intent in intents
                                    if intent.symbol == order.symbol
                                    and intent.action == order.action
                                    and intent.quantity >= order.quantity
                                ),
                                (),
                            )
                        ),
                    }
                )

            for blocked in plan.blocked_intents:
                blocked_intent_rows.append(
                    {
                        "trade_date": str(trade_date),
                        "symbol": blocked.symbol,
                        "action": blocked.action,
                        "requested_quantity": blocked.quantity,
                        "source": blocked.source,
                        "reason": "execution_engine_block",
                    }
                )

            market_value_after = 0.0
            for symbol, qty in positions_qty.items():
                market_state = market_by_symbol.get(symbol)
                if market_state is not None:
                    market_value_after += qty * market_state.last_price
            equity_after = account_cash + market_value_after
            previous_equity = equity_after

            index_context = {}
            for index_symbol in ("000001", "399006", "000688"):
                index_row = index_bars.get((index_symbol, trade_date))
                if index_row is None:
                    continue
                pre_close = float(index_row["pre_close"])
                ret = 0.0 if pre_close <= 0 else float(index_row["close"]) / pre_close - 1.0
                index_context[index_symbol] = {
                    "close": index_row["close"],
                    "day_return": round(ret, 6),
                }

            replay_day_rows.append(
                {
                    "trade_date": str(trade_date),
                    "episode_count": len(day_episode_rows),
                    "intent_count": len(intents),
                    "planned_order_count": len(plan.orders),
                    "blocked_intent_count": len(plan.blocked_intents),
                    "cash_after_close": round(account_cash, 4),
                    "equity_after_close": round(equity_after, 4),
                    "gross_exposure_after_close": round(0.0 if equity_after <= 0 else market_value_after / equity_after, 6),
                    "day_turnover_notional": round(day_turnover, 4),
                    "board_context": self._build_board_context(
                        trade_date=trade_date,
                        board_symbols=board_symbols,
                        daily_bars=daily_bars,
                    ),
                    "index_context": index_context,
                }
            )

        realized_action_modes = sorted({row["action_mode"] for row in executed_order_rows})
        summary = {
            "acceptance_posture": "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1",
            "board_name": "CPO",
            "initial_capital": 1_000_000.0,
            "margin_enabled": False,
            "shorting_enabled": False,
            "t_plus_one_enabled": True,
            "supported_action_modes": supported_action_modes,
            "realized_action_modes": realized_action_modes,
            "execution_main_feed_symbol_count": len(board_symbols),
            "replay_trade_day_count": len(replay_day_rows),
            "episode_action_day_count": len([row for row in replay_day_rows if row["episode_count"] > 0]),
            "executed_order_count": len(executed_order_rows),
            "blocked_intent_count": len(blocked_intent_rows),
            "final_cash": round(account_cash, 4),
            "final_equity": round(previous_equity, 4),
            "recommended_next_posture": "freeze_full_board_cpo_paper_replay_and_then_expand_action_logic_symbol_coverage",
        }
        interpretation = [
            "V1.13V binds the 20-symbol execution main feed into a daily full-board CPO paper replay instead of using the earlier subset-only market source.",
            "Board context is now computed from the entire CPO cohort every trade day, while action logic still only fires where lawful internal episode controls already exist.",
            "This separates full-board market environment coverage from action-logic maturity and gives the execution layer a genuine CPO-only replay surface.",
        ]
        return V113VCPOFullBoardExecutionMainFeedReplayReport(
            summary=summary,
            replay_day_rows=replay_day_rows,
            executed_order_rows=executed_order_rows,
            blocked_intent_rows=blocked_intent_rows,
            interpretation=interpretation,
        )


def write_v113v_cpo_full_board_execution_main_feed_replay_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113VCPOFullBoardExecutionMainFeedReplayReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
