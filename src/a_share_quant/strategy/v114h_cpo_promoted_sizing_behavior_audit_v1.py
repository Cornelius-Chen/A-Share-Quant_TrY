from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from statistics import median
from typing import Any

from a_share_quant.execution.models import (
    ExecutionIntent,
    PositionSnapshot,
)
from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    V114ACPOConstrainedAddReducePolicySearchPilotAnalyzer,
    load_json_report,
    parse_trade_date,
)


@dataclass(slots=True)
class V114HCPOPromotedSizingBehaviorAuditReport:
    summary: dict[str, Any]
    behavior_summary: dict[str, Any]
    top_improved_expression_rows: list[dict[str, Any]]
    remaining_under_exposed_rows: list[dict[str, Any]]
    promoted_action_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "behavior_summary": self.behavior_summary,
            "top_improved_expression_rows": self.top_improved_expression_rows,
            "remaining_under_exposed_rows": self.remaining_under_exposed_rows,
            "promoted_action_rows": self.promoted_action_rows,
            "interpretation": self.interpretation,
        }


class V114HCPOPromotedSizingBehaviorAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.base = V114ACPOConstrainedAddReducePolicySearchPilotAnalyzer(repo_root=repo_root)

    def _simulate_with_daily_audit(
        self,
        *,
        config: dict[str, Any],
        episode_rows: list[dict[str, Any]],
        board_symbols: set[str],
        daily_bars: dict[tuple[str, date], dict[str, Any]],
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
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
        audit_day_rows: list[dict[str, Any]] = []
        action_rows: list[dict[str, Any]] = []

        for trade_date in trade_dates:
            for symbol, qty in list(positions_qty.items()):
                last_buy_date = positions_last_buy_date.get(symbol)
                if qty <= 0:
                    positions_sellable_qty[symbol] = 0
                elif last_buy_date is None or last_buy_date < trade_date:
                    positions_sellable_qty[symbol] = qty

            market_by_symbol = {}
            for symbol in board_symbols | set(positions_qty.keys()):
                market_state = self.base._make_market_state(symbol=symbol, trade_date=trade_date, daily_bars=daily_bars)
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
            board_context = self.base._build_board_context(
                trade_date=trade_date,
                board_symbols=board_symbols,
                daily_bars=daily_bars,
            )
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
                    quantity = self.base._lot_round(delta, market_state.last_price)
                    if quantity > 0:
                        intents.append(
                            ExecutionIntent(
                                trade_date=trade_date,
                                symbol=symbol,
                                action="buy",
                                quantity=quantity,
                                strategy_id="cpo_promoted_default_sizing_audit",
                                source=f"{object_id}:{control_label}",
                                rationale="target_weight_expression_from_promoted_default",
                                tags=(object_id, control_label, row["assistant_confidence_tier"], "open" if current_qty <= 0 else "add"),
                            )
                        )
                elif control_label == "de_risk" and current_qty > 0:
                    desired_value = current_value * float(config["derisk_keep_fraction"])
                    reduce_value = max(0.0, current_value - desired_value)
                    quantity = min(self.base._lot_round(reduce_value, market_state.last_price), current_qty)
                    if quantity > 0:
                        intents.append(
                            ExecutionIntent(
                                trade_date=trade_date,
                                symbol=symbol,
                                action="sell",
                                quantity=quantity,
                                strategy_id="cpo_promoted_default_sizing_audit",
                                source=f"{object_id}:{control_label}",
                                rationale="reduce_to_derisk_band_from_promoted_default",
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
                            strategy_id="cpo_promoted_default_sizing_audit",
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
                    quantity = self.base._lot_round(delta, market_state.last_price)
                    if quantity > 0:
                        intents.append(
                            ExecutionIntent(
                                trade_date=trade_date,
                                symbol=symbol,
                                action="buy",
                                quantity=quantity,
                                strategy_id="cpo_promoted_default_sizing_audit",
                                source=f"{object_id}:board_strength_add",
                                rationale="board_strength_follow_through_add",
                                tags=(object_id, "eligibility", "promoted_default", "add"),
                            )
                        )

            executed_today = 0
            action_mode_counts = {"open": 0, "add": 0, "reduce": 0, "close": 0}
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
                    max_order_qty = self.base._lot_round(300_000.0, market_state.last_price)
                    max_weight_qty = self.base._lot_round(max(0.0, 0.10 * equity - current_value), market_state.last_price)
                    max_cash_qty = self.base._lot_round(account_cash, market_state.last_price)
                    approved_qty = min(intent.quantity, max_order_qty, max_weight_qty, max_cash_qty)
                    if approved_qty <= 0:
                        continue
                    notional = approved_qty * market_state.last_price
                    if notional < 5_000:
                        continue
                    executed_orders += 1
                    executed_today += 1
                    action_mode = "open" if current_qty <= 0 else "add"
                    action_mode_counts[action_mode] += 1
                    positions_qty[intent.symbol] = current_qty + approved_qty
                    positions_sellable_qty[intent.symbol] = positions_sellable_qty.get(intent.symbol, 0)
                    positions_last_buy_date[intent.symbol] = trade_date
                    account_cash -= notional
                    action_rows.append(
                        {
                            "trade_date": str(trade_date),
                            "symbol": intent.symbol,
                            "action_mode": action_mode,
                            "quantity": approved_qty,
                            "price": market_state.last_price,
                            "notional": round(notional, 4),
                            "source": intent.source,
                            "board_strong": board_strong,
                        }
                    )
                elif intent.action == "sell":
                    current_sellable = positions_sellable_qty.get(intent.symbol, current_qty)
                    approved_qty = min(intent.quantity, current_sellable)
                    if approved_qty <= 0:
                        continue
                    notional = approved_qty * market_state.last_price
                    executed_orders += 1
                    executed_today += 1
                    action_mode = "close" if approved_qty == current_qty else "reduce"
                    action_mode_counts[action_mode] += 1
                    positions_qty[intent.symbol] = max(0, current_qty - approved_qty)
                    positions_sellable_qty[intent.symbol] = max(0, current_sellable - approved_qty)
                    if positions_qty[intent.symbol] == 0:
                        positions_last_buy_date[intent.symbol] = None
                    account_cash += notional
                    action_rows.append(
                        {
                            "trade_date": str(trade_date),
                            "symbol": intent.symbol,
                            "action_mode": action_mode,
                            "quantity": approved_qty,
                            "price": market_state.last_price,
                            "notional": round(notional, 4),
                            "source": intent.source,
                            "board_strong": board_strong,
                        }
                    )

            market_value_after = 0.0
            holdings_after: list[str] = []
            for symbol, qty in positions_qty.items():
                market_state = market_by_symbol.get(symbol)
                if market_state is not None and qty > 0:
                    market_value_after += qty * market_state.last_price
                    holdings_after.append(symbol)
            equity_after = account_cash + market_value_after
            gross_exposure_after = 0.0 if equity_after <= 0 else market_value_after / equity_after
            previous_equity = equity_after

            audit_day_rows.append(
                {
                    "trade_date": str(trade_date),
                    "board_avg_return": round(float(board_context["avg_return"]), 6),
                    "board_breadth": round(float(board_context["breadth"]), 6),
                    "board_strong": board_strong,
                    "equity_after_close": round(equity_after, 4),
                    "gross_exposure_after_close": round(gross_exposure_after, 6),
                    "action_count": executed_today,
                    "action_mode_counts": action_mode_counts,
                    "holding_symbols_after_close": sorted(holdings_after),
                }
            )

        board_curve = 1.0
        for row in self.base._replay_day_rows_from_payload:
            board_curve *= 1.0 + float(dict(row["board_context"]).get("avg_return", 0.0))
        final_curve = previous_equity / 1_000_000.0
        capture_ratio = 0.0 if board_curve <= 1.0 else (final_curve - 1.0) / (board_curve - 1.0)
        score = (final_curve - 1.0) - 1.5 * max_drawdown + 0.35 * capture_ratio - 0.0025 * executed_orders - 0.25 * under_exposure_penalty

        summary_row = {
            "config": config,
            "final_curve": round(final_curve, 4),
            "max_drawdown": round(max_drawdown, 4),
            "capture_ratio_vs_board": round(capture_ratio, 4),
            "executed_order_count": executed_orders,
            "under_exposure_penalty": round(under_exposure_penalty, 4),
            "score": round(score, 6),
        }
        return summary_row, audit_day_rows, action_rows

    def analyze(
        self,
        *,
        v113n_payload: dict[str, Any],
        v113v_payload: dict[str, Any],
        v114e_payload: dict[str, Any],
    ) -> V114HCPOPromotedSizingBehaviorAuditReport:
        summary_n = dict(v113n_payload.get("summary", {}))
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_e = dict(v114e_payload.get("summary", {}))
        if str(summary_n.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.14H expects V1.13N real board episode population.")
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14H expects V1.13V baseline replay.")
        if str(summary_e.get("acceptance_posture")) != "freeze_v114e_cpo_default_sizing_replay_promotion_v1":
            raise ValueError("V1.14H expects V1.14E default sizing replay promotion.")

        self.base._replay_day_rows_from_payload = list(v113v_payload.get("replay_day_rows", []))
        episode_rows = list(v113n_payload.get("internal_point_rows", []))
        board_symbols = {
            "300308", "300502", "300394", "002281", "603083", "688205", "301205", "300570",
            "688498", "688313", "300757", "601869", "600487", "600522", "000070", "603228",
            "001267", "300620", "300548", "000988",
        }
        daily_bars = self.base._load_daily_bars(
            self.repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv"
        )
        promoted_config = dict(v114e_payload.get("promoted_default_row", {}).get("config", {}))
        promoted_summary_row, promoted_day_rows, promoted_action_rows = self._simulate_with_daily_audit(
            config=promoted_config,
            episode_rows=episode_rows,
            board_symbols=board_symbols,
            daily_bars=daily_bars,
        )

        baseline_day_map = {
            str(row["trade_date"]): row for row in list(v113v_payload.get("replay_day_rows", []))
        }

        improved_rows: list[dict[str, Any]] = []
        remaining_under_exposed_rows: list[dict[str, Any]] = []
        strong_board_days = 0
        improved_expression_days = 0
        for promoted_row in promoted_day_rows:
            trade_date = str(promoted_row["trade_date"])
            baseline_row = baseline_day_map.get(trade_date)
            if baseline_row is None:
                continue
            base_exposure = float(baseline_row["gross_exposure_after_close"])
            promoted_exposure = float(promoted_row["gross_exposure_after_close"])
            board_avg = float(promoted_row["board_avg_return"])
            board_breadth = float(promoted_row["board_breadth"])
            exposure_delta = promoted_exposure - base_exposure
            if bool(promoted_row["board_strong"]):
                strong_board_days += 1
                if exposure_delta > 0.05:
                    improved_expression_days += 1
                    improved_rows.append(
                        {
                            "trade_date": trade_date,
                            "board_avg_return": round(board_avg, 6),
                            "board_breadth": round(board_breadth, 6),
                            "baseline_exposure": round(base_exposure, 6),
                            "promoted_exposure": round(promoted_exposure, 6),
                            "exposure_delta": round(exposure_delta, 6),
                            "action_count": int(promoted_row["action_count"]),
                            "holding_symbols_after_close": list(promoted_row["holding_symbols_after_close"]),
                        }
                    )
                if promoted_exposure < float(promoted_config["under_exposure_floor"]):
                    remaining_under_exposed_rows.append(
                        {
                            "trade_date": trade_date,
                            "board_avg_return": round(board_avg, 6),
                            "board_breadth": round(board_breadth, 6),
                            "promoted_exposure": round(promoted_exposure, 6),
                            "under_exposure_gap": round(float(promoted_config["under_exposure_floor"]) - promoted_exposure, 6),
                            "action_count": int(promoted_row["action_count"]),
                            "holding_symbols_after_close": list(promoted_row["holding_symbols_after_close"]),
                        }
                    )

        top_improved_expression_rows = sorted(
            improved_rows,
            key=lambda row: (row["exposure_delta"], row["board_avg_return"]),
            reverse=True,
        )[:10]
        remaining_under_exposed_rows = sorted(
            remaining_under_exposed_rows,
            key=lambda row: (row["under_exposure_gap"], row["board_avg_return"]),
            reverse=True,
        )[:10]

        behavior_summary = {
            "strong_board_day_count": strong_board_days,
            "improved_expression_day_count": improved_expression_days,
            "remaining_under_exposed_strong_day_count": len(
                [row for row in promoted_day_rows if bool(row["board_strong"]) and float(row["gross_exposure_after_close"]) < float(promoted_config["under_exposure_floor"])]
            ),
            "promoted_action_count": len(promoted_action_rows),
            "add_like_action_count": len([row for row in promoted_action_rows if row["action_mode"] == "add"]),
            "reduce_like_action_count": len([row for row in promoted_action_rows if row["action_mode"] == "reduce"]),
        }

        summary = {
            "acceptance_posture": "freeze_v114h_cpo_promoted_sizing_behavior_audit_v1",
            "baseline_curve": round(float(summary_e.get("baseline_curve", 0.0)), 4),
            "promoted_curve": round(float(promoted_summary_row["final_curve"]), 4),
            "baseline_max_drawdown": round(float(summary_e.get("baseline_max_drawdown", 0.0)), 4),
            "promoted_max_drawdown": round(float(promoted_summary_row["max_drawdown"]), 4),
            "strong_board_day_count": strong_board_days,
            "improved_expression_day_count": improved_expression_days,
            "remaining_under_exposed_strong_day_count": behavior_summary["remaining_under_exposed_strong_day_count"],
            "recommended_next_posture": "use_v114h_behavior_audit_to_target_next_add_reduce_and_market_voice_learning",
        }
        interpretation = [
            "V1.14H audits the promoted default sizing candidate day by day instead of only comparing end-point curves.",
            "The goal is to isolate where promoted sizing actually fixed under-exposure, where it still leaves too much board strength uncaptured, and where stronger expression might be crossing into unnecessary aggression.",
            "This converts the sizing promotion from a parameter result into an observable daily behavior profile that can guide the next market-voice and state-transition learning steps.",
        ]

        return V114HCPOPromotedSizingBehaviorAuditReport(
            summary=summary,
            behavior_summary=behavior_summary,
            top_improved_expression_rows=top_improved_expression_rows,
            remaining_under_exposed_rows=remaining_under_exposed_rows,
            promoted_action_rows=promoted_action_rows,
            interpretation=interpretation,
        )


def write_v114h_cpo_promoted_sizing_behavior_audit_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114HCPOPromotedSizingBehaviorAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path

