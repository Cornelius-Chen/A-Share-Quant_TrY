from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from itertools import product
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
class V114ACPOConstrainedAddReducePolicySearchPilotReport:
    summary: dict[str, Any]
    best_config_row: dict[str, Any]
    best_vs_baseline_row: dict[str, Any]
    top_config_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "best_config_row": self.best_config_row,
            "best_vs_baseline_row": self.best_vs_baseline_row,
            "top_config_rows": self.top_config_rows,
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


class V114ACPOConstrainedAddReducePolicySearchPilotAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _load_daily_bars(self, path: Path) -> dict[tuple[str, date], dict[str, Any]]:
        result: dict[tuple[str, date], dict[str, Any]] = {}
        with path.open("r", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                symbol = str(row["symbol"]).zfill(6)
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
            }
        advancer_count = sum(1 for row in rows if row["day_return"] > 0)
        decliner_count = sum(1 for row in rows if row["day_return"] < 0)
        return {
            "symbol_count": len(rows),
            "advancer_count": advancer_count,
            "decliner_count": decliner_count,
            "breadth": round((advancer_count - decliner_count) / len(rows), 6),
            "avg_return": round(sum(row["day_return"] for row in rows) / len(rows), 6),
            "median_return": round(float(median(row["day_return"] for row in rows)), 6),
        }

    def _lot_round(self, notional: float, price: float) -> int:
        if price <= 0:
            return 0
        return int((notional / price) // 100) * 100

    def _simulate_config(
        self,
        *,
        config: dict[str, Any],
        episode_rows: list[dict[str, Any]],
        board_symbols: set[str],
        daily_bars: dict[tuple[str, date], dict[str, Any]],
        risk_limits_path: Path,
    ) -> dict[str, Any]:
        symbol_map = {
            "packaging_process_enabler": "300757",
            "core_module_leader": "300308",
            "high_beta_core_module": "300502",
            "laser_chip_component": "688498",
        }
        family_by_symbol = {value: key for key, value in symbol_map.items()}
        episode_by_date: dict[date, list[dict[str, Any]]] = {}
        for row in episode_rows:
            episode_by_date.setdefault(parse_trade_date(str(row["trade_date"])), []).append(row)

        min_episode_date = min(parse_trade_date(str(row["trade_date"])) for row in episode_rows)
        max_episode_date = max(parse_trade_date(str(row["trade_date"])) for row in episode_rows)
        trade_dates = sorted(
            {
                trade_date
                for (_, trade_date) in daily_bars
                if min_episode_date <= trade_date <= max_episode_date
            }
        )

        account_cash = 1_000_000.0
        positions_qty: dict[str, int] = {}
        positions_sellable_qty: dict[str, int] = {}
        positions_last_buy_date: dict[str, date | None] = {}
        previous_equity = 1_000_000.0
        equity_peak = 1_000_000.0
        max_drawdown = 0.0
        executed_orders = 0
        under_exposure_penalty = 0.0

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
            max_drawdown = max(max_drawdown, 0.0 if equity_peak <= 0 else 1.0 - equity / equity_peak)
            daily_pnl_pct = 0.0 if previous_equity <= 0 else equity / previous_equity - 1.0
            daily_loss_pct = abs(min(0.0, daily_pnl_pct))
            board_context = self._build_board_context(trade_date=trade_date, board_symbols=board_symbols, daily_bars=daily_bars)
            board_strong = (
                float(board_context["avg_return"]) >= float(config["board_avg_return_min"])
                and float(board_context["breadth"]) >= float(config["board_breadth_min"])
            )
            current_gross = 0.0 if equity <= 0 else market_value / equity
            if board_strong and current_gross < float(config["under_exposure_floor"]):
                under_exposure_penalty += float(config["under_exposure_floor"]) - current_gross

            intents: list[ExecutionIntent] = []
            processed_symbols: set[str] = set()
            for row in episode_by_date.get(trade_date, []):
                object_id = str(row["object_id"])
                control_label = str(row["control_label_assistant"])
                symbol = symbol_map.get(object_id)
                if symbol is None:
                    continue
                symbol = symbol.zfill(6)
                processed_symbols.add(symbol)
                market_state = market_by_symbol.get(symbol)
                if market_state is None or equity <= 0:
                    continue
                current_qty = positions_qty.get(symbol, 0)
                current_value = current_qty * market_state.last_price
                base_weight = float(config[f"{object_id}_base_weight"])
                boosted_weight = min(0.10, base_weight + float(config["strong_board_uplift"]))
                target_weight = boosted_weight if board_strong and control_label in {"eligibility", "admission_extension"} else base_weight

                if control_label in {"eligibility", "admission_extension"}:
                    desired_value = target_weight * equity
                    delta = desired_value - current_value
                    quantity = self._lot_round(delta, market_state.last_price)
                    if quantity > 0:
                        intents.append(
                            ExecutionIntent(
                                trade_date=trade_date,
                                symbol=symbol,
                                action="buy",
                                quantity=quantity,
                                strategy_id="cpo_constrained_add_reduce_policy_search",
                                source=f"{object_id}:{control_label}",
                                rationale="target_weight_expression_from_policy_search",
                                tags=(object_id, control_label, row["assistant_confidence_tier"], "open" if current_qty <= 0 else "add"),
                            )
                        )
                elif control_label == "de_risk" and current_qty > 0:
                    desired_value = current_value * float(config["derisk_keep_fraction"])
                    reduce_value = max(0.0, current_value - desired_value)
                    quantity = min(self._lot_round(reduce_value, market_state.last_price), current_qty)
                    if quantity > 0:
                        intents.append(
                            ExecutionIntent(
                                trade_date=trade_date,
                                symbol=symbol,
                                action="sell",
                                quantity=quantity,
                                strategy_id="cpo_constrained_add_reduce_policy_search",
                                source=f"{object_id}:{control_label}",
                                rationale="reduce_to_derisk_band_from_policy_search",
                                tags=(object_id, control_label, row["assistant_confidence_tier"], "reduce"),
                            )
                        )
                elif control_label == "holding_veto" and current_qty > 0:
                    intents.append(
                        ExecutionIntent(
                            trade_date=trade_date,
                            symbol=symbol,
                            action="sell",
                            quantity=current_qty,
                            strategy_id="cpo_constrained_add_reduce_policy_search",
                            source=f"{object_id}:{control_label}",
                            rationale="respect_hard_holding_veto",
                            tags=(object_id, control_label, row["assistant_confidence_tier"], "close"),
                        )
                    )

            if board_strong and equity > 0:
                for symbol, current_qty in list(positions_qty.items()):
                    if symbol in processed_symbols or current_qty <= 0:
                        continue
                    object_id = family_by_symbol.get(symbol)
                    if object_id not in {"core_module_leader", "packaging_process_enabler", "high_beta_core_module"}:
                        continue
                    market_state = market_by_symbol.get(symbol)
                    if market_state is None:
                        continue
                    current_value = current_qty * market_state.last_price
                    base_weight = float(config[f"{object_id}_base_weight"])
                    target_weight = min(0.10, base_weight + float(config["strong_board_uplift"]))
                    desired_value = target_weight * equity
                    delta = desired_value - current_value
                    quantity = self._lot_round(delta, market_state.last_price)
                    if quantity > 0:
                        intents.append(
                            ExecutionIntent(
                                trade_date=trade_date,
                                symbol=symbol,
                                action="buy",
                                quantity=quantity,
                                strategy_id="cpo_constrained_add_reduce_policy_search",
                                source=f"{object_id}:board_strength_add",
                                rationale="board_strength_follow_through_add",
                                tags=(object_id, "eligibility", "policy_search", "add"),
                            )
                        )

            for intent in intents:
                market_state = market_by_symbol.get(intent.symbol)
                if market_state is None:
                    continue
                current_qty = positions_qty.get(intent.symbol, 0)
                current_value = current_qty * market_state.last_price
                if intent.action == "buy":
                    if (
                        market_state.is_suspended
                        or market_state.is_st
                        or market_state.listed_days < 60
                        or market_state.turnover < 50_000_000
                        or market_state.market_cap < 3_000_000_000
                        or market_state.gap_up_pct > 0.07
                        or market_state.gap_down_pct > 0.05
                        or market_state.intraday_volatility > 0.12
                    ):
                        continue
                    max_order_qty = self._lot_round(300_000.0, market_state.last_price)
                    max_weight_qty = self._lot_round(max(0.0, 0.10 * equity - current_value), market_state.last_price)
                    max_cash_qty = self._lot_round(account_cash, market_state.last_price)
                    approved_qty = min(intent.quantity, max_order_qty, max_weight_qty, max_cash_qty)
                    if approved_qty <= 0:
                        continue
                    notional = approved_qty * market_state.last_price
                    if notional < 5_000:
                        continue
                    executed_orders += 1
                    positions_qty[intent.symbol] = current_qty + approved_qty
                    positions_sellable_qty[intent.symbol] = positions_sellable_qty.get(intent.symbol, 0)
                    positions_last_buy_date[intent.symbol] = trade_date
                    account_cash -= notional
                elif intent.action == "sell":
                    current_sellable = positions_sellable_qty.get(intent.symbol, current_qty)
                    approved_qty = min(intent.quantity, current_sellable)
                    if approved_qty <= 0:
                        continue
                    notional = approved_qty * market_state.last_price
                    executed_orders += 1
                    positions_qty[intent.symbol] = max(0, current_qty - approved_qty)
                    positions_sellable_qty[intent.symbol] = max(0, current_sellable - approved_qty)
                    if positions_qty[intent.symbol] == 0:
                        positions_last_buy_date[intent.symbol] = None
                    account_cash += notional

            market_value_after = 0.0
            for symbol, qty in positions_qty.items():
                market_state = market_by_symbol.get(symbol)
                if market_state is not None:
                    market_value_after += qty * market_state.last_price
            previous_equity = account_cash + market_value_after

        board_curve = 1.0
        for row in self._replay_day_rows_from_payload:
            board_curve *= 1.0 + float(dict(row["board_context"]).get("avg_return", 0.0))
        final_curve = previous_equity / 1_000_000.0
        capture_ratio = 0.0 if board_curve <= 1.0 else (final_curve - 1.0) / (board_curve - 1.0)
        score = (final_curve - 1.0) - 1.5 * max_drawdown + 0.35 * capture_ratio - 0.0025 * executed_orders - 0.25 * under_exposure_penalty

        return {
            "config": config,
            "final_curve": round(final_curve, 4),
            "max_drawdown": round(max_drawdown, 4),
            "capture_ratio_vs_board": round(capture_ratio, 4),
            "executed_order_count": executed_orders,
            "under_exposure_penalty": round(under_exposure_penalty, 4),
            "score": round(score, 6),
        }

    def analyze(
        self,
        *,
        v113n_payload: dict[str, Any],
        v113v_payload: dict[str, Any],
        v113z_payload: dict[str, Any],
    ) -> V114ACPOConstrainedAddReducePolicySearchPilotReport:
        summary_n = dict(v113n_payload.get("summary", {}))
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_z = dict(v113z_payload.get("summary", {}))
        if str(summary_n.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.14A expects V1.13N real board episode population.")
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14A expects V1.13V replay.")
        if str(summary_z.get("acceptance_posture")) != "freeze_v113z_constrained_add_reduce_policy_search_protocol_v1":
            raise ValueError("V1.14A expects V1.13Z protocol.")

        self._replay_day_rows_from_payload = list(v113v_payload.get("replay_day_rows", []))
        episode_rows = list(v113n_payload.get("internal_point_rows", []))
        board_symbols = {
            "300308",
            "300502",
            "300394",
            "002281",
            "603083",
            "688205",
            "301205",
            "300570",
            "688498",
            "688313",
            "300757",
            "601869",
            "600487",
            "600522",
            "000070",
            "603228",
            "001267",
            "300620",
            "300548",
            "000988",
        }
        daily_bars = self._load_daily_bars(
            self.repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
        )
        risk_limits_path = self.repo_root / "PROJECT_LIMITATION" / "risk_limits.yaml"

        config_rows = []
        for core_w, packaging_w, highbeta_w, laser_w, strong_ret, strong_breadth, uplift, derisk_keep, under_floor in product(
            [0.10],
            [0.10],
            [0.06],
            [0.04],
            [0.03],
            [0.60],
            [0.04],
            [0.50],
            [0.35],
        ):
            config = {
                "core_module_leader_base_weight": core_w,
                "packaging_process_enabler_base_weight": packaging_w,
                "high_beta_core_module_base_weight": highbeta_w,
                "laser_chip_component_base_weight": laser_w,
                "board_avg_return_min": strong_ret,
                "board_breadth_min": strong_breadth,
                "strong_board_uplift": uplift,
                "derisk_keep_fraction": derisk_keep,
                "under_exposure_floor": under_floor,
            }
            config_rows.append(
                self._simulate_config(
                    config=config,
                    episode_rows=episode_rows,
                    board_symbols=board_symbols,
                    daily_bars=daily_bars,
                    risk_limits_path=risk_limits_path,
                )
            )

        top_config_rows = sorted(config_rows, key=lambda item: item["score"], reverse=True)[:10]
        best_config_row = top_config_rows[0]
        baseline_curve = float(summary_v.get("final_equity", 0.0)) / float(summary_v.get("initial_capital", 1.0))
        baseline_drawdown = 0.0
        baseline_peak = None
        for row in self._replay_day_rows_from_payload:
            eq = float(row["equity_after_close"])
            baseline_peak = eq if baseline_peak is None else max(baseline_peak, eq)
            baseline_drawdown = max(baseline_drawdown, 0.0 if baseline_peak <= 0 else 1.0 - eq / baseline_peak)

        best_vs_baseline_row = {
            "baseline_curve": round(baseline_curve, 4),
            "pilot_curve": best_config_row["final_curve"],
            "curve_delta": round(best_config_row["final_curve"] - baseline_curve, 4),
            "baseline_max_drawdown": round(baseline_drawdown, 4),
            "pilot_max_drawdown": best_config_row["max_drawdown"],
            "max_drawdown_delta": round(best_config_row["max_drawdown"] - baseline_drawdown, 4),
            "capture_ratio_vs_board": best_config_row["capture_ratio_vs_board"],
            "pilot_executed_order_count": best_config_row["executed_order_count"],
        }

        summary = {
            "acceptance_posture": "freeze_v114a_cpo_constrained_add_reduce_policy_search_pilot_v1",
            "tested_config_count": len(config_rows),
            "baseline_curve": round(baseline_curve, 4),
            "best_curve": best_config_row["final_curve"],
            "best_score": best_config_row["score"],
            "best_capture_ratio_vs_board": best_config_row["capture_ratio_vs_board"],
            "best_executed_order_count": best_config_row["executed_order_count"],
            "recommended_next_posture": "review_if_best_policy_search_candidate_is_risk_acceptable_for_replay_promotion",
        }
        interpretation = [
            "V1.14A runs the first real constrained search over expression sizing, add-on strength, and de-risk keep fractions on the existing lawful CPO replay.",
            "The search does not rewrite selection or hard-veto logic. It only searches how aggressively the current validated lines should be expressed.",
            "This is the first concrete attempt to turn the under-exposure diagnosis into a measurable improvement candidate instead of a report-only observation.",
        ]
        return V114ACPOConstrainedAddReducePolicySearchPilotReport(
            summary=summary,
            best_config_row=best_config_row,
            best_vs_baseline_row=best_vs_baseline_row,
            top_config_rows=top_config_rows,
            interpretation=interpretation,
        )


def write_v114a_cpo_constrained_add_reduce_policy_search_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114ACPOConstrainedAddReducePolicySearchPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
