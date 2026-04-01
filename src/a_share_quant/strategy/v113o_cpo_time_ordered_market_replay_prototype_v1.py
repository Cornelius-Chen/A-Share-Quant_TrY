from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from a_share_quant.execution.engine import ExecutionEngine
from a_share_quant.execution.models import (
    AccountSnapshot,
    ExecutionIntent,
    PositionSnapshot,
    SymbolMarketState,
)


@dataclass(slots=True)
class V113OCPOTimeOrderedMarketReplayPrototypeReport:
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
    if symbol.startswith("300") or symbol.startswith("301"):
        return "ChiNext"
    return "MainBoard"


class V113OCPOTimeOrderedMarketReplayPrototypeAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _load_daily_bars(self, path: Path, symbols: set[str]) -> dict[tuple[str, date], dict[str, Any]]:
        result: dict[tuple[str, date], dict[str, Any]] = {}
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                symbol = str(row["symbol"])
                if symbol not in symbols:
                    continue
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

    def _load_stock_snapshots(self, path: Path, symbols: set[str]) -> dict[tuple[str, date], dict[str, Any]]:
        result: dict[tuple[str, date], dict[str, Any]] = {}
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                symbol = str(row["symbol"])
                if symbol not in symbols:
                    continue
                trade_date = parse_trade_date(str(row["trade_date"]))
                result[(symbol, trade_date)] = {
                    "expected_upside": float(row["expected_upside"]),
                    "drive_strength": float(row["drive_strength"]),
                    "stability": float(row["stability"]),
                    "liquidity": float(row["liquidity"]),
                    "late_mover_quality": float(row["late_mover_quality"]),
                    "resonance": float(row["resonance"]),
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
        gap_up = 0.0
        gap_down = 0.0
        if prev_close > 0:
            open_pct = (float(row["open"]) / prev_close) - 1.0
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

    def analyze(
        self,
        *,
        v113n_payload: dict[str, Any],
    ) -> V113OCPOTimeOrderedMarketReplayPrototypeReport:
        n_summary = dict(v113n_payload.get("summary", {}))
        if str(n_summary.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.13O expects V1.13N real episode population first.")

        all_internal_rows = list(v113n_payload.get("internal_point_rows", []))
        replay_rows = [
            row
            for row in all_internal_rows
            if parse_trade_date(str(row["trade_date"])).year == 2024
        ]
        if not replay_rows:
            raise ValueError("V1.13O found no 2024 CPO rows to replay.")

        raw_daily_path = self.repo_root / "data" / "raw" / "daily_bars" / "akshare_daily_bars_market_research_v1.csv"
        stock_snapshot_path = self.repo_root / "data" / "derived" / "stock_snapshots" / "market_research_stock_snapshots_v1.csv"
        index_path = self.repo_root / "data" / "raw" / "index_daily_bars" / "akshare_index_daily_bars_market_research_v1.csv"
        risk_limits_path = self.repo_root / "PROJECT_LIMITATION" / "risk_limits.yaml"

        traded_symbols = {str(row["object_id"]) for row in replay_rows}
        symbol_map = {
            "packaging_process_enabler": "300757",
            "core_module_leader": "300308",
            "high_beta_core_module": "300502",
            "laser_chip_component": "688498",
        }
        replay_symbols = {symbol_map[obj] for obj in traded_symbols if obj in symbol_map}

        daily_bars = self._load_daily_bars(raw_daily_path, replay_symbols)
        stock_snapshots = self._load_stock_snapshots(stock_snapshot_path, replay_symbols)
        index_bars = self._load_index_bars(index_path, {"000001", "399006", "000688"})
        engine = ExecutionEngine(risk_limits_path=risk_limits_path)

        trade_dates = sorted({parse_trade_date(str(row["trade_date"])) for row in replay_rows})
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
                    continue
                if last_buy_date is None or last_buy_date < trade_date:
                    positions_sellable_qty[symbol] = qty

            market_by_symbol: dict[str, SymbolMarketState] = {}
            symbols_in_scope = {
                symbol_map[str(row["object_id"])]
                for row in replay_rows
                if parse_trade_date(str(row["trade_date"])) == trade_date and str(row["object_id"]) in symbol_map
            }
            for symbol in symbols_in_scope | set(positions_qty.keys()):
                state = self._make_market_state(
                    symbol=symbol,
                    trade_date=trade_date,
                    daily_bars=daily_bars,
                )
                if state is not None:
                    market_by_symbol[symbol] = state

            market_value = 0.0
            positions_by_symbol: dict[str, PositionSnapshot] = {}
            for symbol, qty in positions_qty.items():
                market_state = market_by_symbol.get(symbol)
                if market_state is None:
                    continue
                value = qty * market_state.last_price
                market_value += value
            equity = account_cash + market_value
            equity_peak = max(equity_peak, equity)
            daily_pnl_pct = 0.0
            if previous_equity > 0:
                daily_pnl_pct = (equity / previous_equity) - 1.0
            daily_loss_pct = abs(min(0.0, daily_pnl_pct))
            strategy_drawdown_pct = 0.0 if equity_peak <= 0 else max(0.0, 1.0 - (equity / equity_peak))

            for symbol, qty in positions_qty.items():
                market_state = market_by_symbol.get(symbol)
                if market_state is None or equity <= 0:
                    continue
                value = qty * market_state.last_price
                positions_by_symbol[symbol] = PositionSnapshot(
                    symbol=symbol,
                    quantity=qty,
                    market_value=value,
                    strategy_weight=value / equity,
                    account_weight=value / equity,
                    add_count_today=0,
                    order_count_today=0,
                    sellable_quantity=positions_sellable_qty.get(symbol, qty),
                    last_buy_trade_date=positions_last_buy_date.get(symbol),
                )

            account = AccountSnapshot(
                trade_date=trade_date,
                account_id="cpo_paper_1m",
                cash=account_cash,
                equity=equity,
                gross_exposure=0.0 if equity <= 0 else market_value / equity,
                net_exposure=0.0 if equity <= 0 else market_value / equity,
                daily_turnover=0.0,
                daily_loss_pct=daily_loss_pct,
                strategy_drawdown_pct=strategy_drawdown_pct,
                account_drawdown_pct=strategy_drawdown_pct,
                open_order_count=0,
                open_position_count=len([q for q in positions_qty.values() if q > 0]),
            )

            day_rows = [row for row in replay_rows if parse_trade_date(str(row["trade_date"])) == trade_date]
            intents: list[ExecutionIntent] = []
            for row in day_rows:
                object_id = str(row["object_id"])
                symbol = symbol_map[object_id]
                control_label = str(row["control_label_assistant"])
                confidence_tier = str(row["assistant_confidence_tier"])
                qty_held = positions_qty.get(symbol, 0)
                market_state = market_by_symbol.get(symbol)
                if market_state is None:
                    intents.append(
                        ExecutionIntent(
                            trade_date=trade_date,
                            symbol=symbol,
                            action="buy",
                            quantity=0,
                            strategy_id="cpo_board_replay",
                            source=f"{object_id}:{control_label}",
                            rationale="market_state_missing_in_local_dataset",
                            tags=(object_id, control_label, confidence_tier, "blocked_for_missing_market_state"),
                        )
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
                                strategy_id="cpo_board_replay",
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
                                    strategy_id="cpo_board_replay",
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
                            strategy_id="cpo_board_replay",
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
                            strategy_id="cpo_board_replay",
                            source=f"{object_id}:{control_label}",
                            rationale="close_from_holding_veto",
                            tags=(object_id, control_label, confidence_tier, "close"),
                        )
                    )

            normalized_intents = [
                intent
                for intent in intents
                if not (intent.quantity <= 0 and "blocked_for_missing_market_state" not in intent.tags)
            ]

            synthetic_blocked = [intent for intent in normalized_intents if "blocked_for_missing_market_state" in intent.tags]
            executable_intents = [intent for intent in normalized_intents if "blocked_for_missing_market_state" not in intent.tags]

            plan = engine.build_plan(
                intents=executable_intents,
                account=account,
                positions_by_symbol=positions_by_symbol,
                market_by_symbol=market_by_symbol,
            )

            day_turnover = 0.0
            for intent in synthetic_blocked:
                blocked_intent_rows.append(
                    {
                        "trade_date": str(trade_date),
                        "symbol": intent.symbol,
                        "action": intent.action,
                        "requested_quantity": intent.quantity,
                        "source": intent.source,
                        "reason": "market_state_missing_in_local_dataset",
                    }
                )

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
                        "action_mode": "open"
                        if order.action == "buy" and positions_by_symbol.get(order.symbol) is None
                        else "add"
                        if order.action == "buy"
                        else "close"
                        if positions_qty.get(order.symbol, 0) == 0
                        else "reduce",
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
                ret = 0.0
                if float(index_row["pre_close"]) > 0:
                    ret = float(index_row["close"]) / float(index_row["pre_close"]) - 1.0
                index_context[index_symbol] = {
                    "close": index_row["close"],
                    "day_return": round(ret, 6),
                }

            advisory_rows = []
            for symbol in symbols_in_scope:
                snap = stock_snapshots.get((symbol, trade_date))
                if snap is not None:
                    advisory_rows.append({"symbol": symbol, **snap})

            replay_day_rows.append(
                {
                    "trade_date": str(trade_date),
                    "episode_count": len(day_rows),
                    "intent_count": len(normalized_intents),
                    "planned_order_count": len(plan.orders),
                    "blocked_intent_count": len(plan.blocked_intents) + len(synthetic_blocked),
                    "cash_after_close": round(account_cash, 4),
                    "equity_after_close": round(equity_after, 4),
                    "gross_exposure_after_close": round(0.0 if equity_after <= 0 else market_value_after / equity_after, 6),
                    "day_turnover_notional": round(day_turnover, 4),
                    "index_context": index_context,
                    "advisory_stock_snapshots": advisory_rows,
                }
            )

        realized_action_modes = sorted({row["action_mode"] for row in executed_order_rows})
        summary = {
            "acceptance_posture": "freeze_v113o_cpo_time_ordered_market_replay_prototype_v1",
            "board_name": "CPO",
            "initial_capital": 1_000_000.0,
            "margin_enabled": False,
            "shorting_enabled": False,
            "t_plus_one_enabled": True,
            "supported_action_modes": supported_action_modes,
            "realized_action_modes": realized_action_modes,
            "replay_trade_day_count": len(replay_day_rows),
            "executed_order_count": len(executed_order_rows),
            "blocked_intent_count": len(blocked_intent_rows),
            "final_cash": round(account_cash, 4),
            "final_equity": round(previous_equity, 4),
            "recommended_next_posture": "connect_more_cpo_symbol_price_feeds_and_then_upgrade_from_subset_replay_to_full_cpo_market_environment_replay",
        }
        interpretation = [
            "V1.13O is the first time-ordered CPO market replay prototype with a real execution engine, initial capital, and explicit no-margin posture.",
            "The prototype only trades symbols with lawful local market data. Missing-feed CPO objects are preserved as blocked intents instead of being silently dropped.",
            "This is still paper replay, but it already combines board episodes, market context, execution gating, and position accounting in one daily loop.",
        ]
        return V113OCPOTimeOrderedMarketReplayPrototypeReport(
            summary=summary,
            replay_day_rows=replay_day_rows,
            executed_order_rows=executed_order_rows,
            blocked_intent_rows=blocked_intent_rows,
            interpretation=interpretation,
        )


def write_v113o_cpo_time_ordered_market_replay_prototype_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V113OCPOTimeOrderedMarketReplayPrototypeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
