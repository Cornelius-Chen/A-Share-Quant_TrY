from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC
from pathlib import Path
from statistics import mean
from typing import Any

from a_share_quant.execution.models import ExecutionIntent, PositionSnapshot
from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    V114ACPOConstrainedAddReducePolicySearchPilotAnalyzer,
    parse_trade_date,
)


@dataclass(slots=True)
class V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayReport:
    summary: dict[str, Any]
    candidate_policy_summary: dict[str, Any]
    top_newly_improved_rows: list[dict[str, Any]]
    remaining_under_exposed_rows: list[dict[str, Any]]
    candidate_action_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "candidate_policy_summary": self.candidate_policy_summary,
            "top_newly_improved_rows": self.top_newly_improved_rows,
            "remaining_under_exposed_rows": self.remaining_under_exposed_rows,
            "candidate_action_rows": self.candidate_action_rows,
            "interpretation": self.interpretation,
        }


class V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.base = V114ACPOConstrainedAddReducePolicySearchPilotAnalyzer(repo_root=repo_root)

    @staticmethod
    def _clip01(value: float) -> float:
        return min(1.0, max(0.0, value))

    def _compute_candidate_scores(
        self,
        *,
        board_context: dict[str, Any],
        previous_board_contexts: list[dict[str, Any]],
        current_gross: float,
        holding_count: int,
        base_floor: float,
    ) -> dict[str, float]:
        avg_return = float(board_context.get("avg_return", 0.0))
        breadth = float(board_context.get("breadth", 0.0))
        top3 = float(board_context.get("top3_turnover_ratio", 0.0))
        recent_window = previous_board_contexts[-5:]
        prev_strong_count_5d = sum(
            1
            for prev in recent_window
            if float(prev.get("avg_return", 0.0)) >= 0.05 and float(prev.get("breadth", 0.0)) >= 0.8
        )
        prev_avg = mean(float(prev.get("avg_return", 0.0)) for prev in recent_window) if recent_window else 0.0
        prev_breadth = mean(float(prev.get("breadth", 0.0)) for prev in recent_window) if recent_window else 0.0

        avg_return_norm = self._clip01((avg_return - 0.05) / 0.08)
        breadth_norm = self._clip01((breadth - 0.8) / 0.2)
        prev_strong_norm = self._clip01(prev_strong_count_5d / 3.0)
        top3_norm = self._clip01((top3 - 0.45) / 0.10)
        avg_accel_norm = self._clip01((avg_return - prev_avg) / 0.08)
        breadth_accel_norm = self._clip01((breadth - prev_breadth) / 0.60)

        market_voice_score = (
            0.30 * avg_return_norm
            + 0.20 * breadth_norm
            + 0.30 * prev_strong_norm
            + 0.20 * top3_norm
        )
        state_transition_score = (
            0.40 * avg_accel_norm
            + 0.35 * breadth_accel_norm
            + 0.25 * prev_strong_norm
        )
        coverage_gap_score = max(0.0, base_floor - current_gross) + 0.03 * max(0, 3 - holding_count)
        combined_add_readiness = (
            0.45 * market_voice_score
            + 0.35 * state_transition_score
            + 0.20 * coverage_gap_score
        )
        return {
            "market_voice_score": round(market_voice_score, 6),
            "state_transition_score": round(state_transition_score, 6),
            "coverage_gap_score": round(coverage_gap_score, 6),
            "combined_add_readiness": round(combined_add_readiness, 6),
            "prev_strong_count_5d": float(prev_strong_count_5d),
        }

    def _resolve_add_confirmation_offset(
        self,
        *,
        config: dict[str, Any],
        scores: dict[str, float],
        holding_count: int,
    ) -> float:
        base_offset = float(config.get("add_confirmation_offset", 0.0))
        mode = str(config.get("add_confirmation_mode", "constant"))
        prev_strong_count = float(scores.get("prev_strong_count_5d", 0.0))
        market_voice_score = float(scores.get("market_voice_score", 0.0))
        state_transition_score = float(scores.get("state_transition_score", 0.0))
        combined_add_readiness = float(scores.get("combined_add_readiness", 0.0))
        threshold = float(config.get("candidate_add_threshold", 0.0))

        if mode == "constant":
            return base_offset
        if mode == "persistence_relaxed":
            return 0.0 if prev_strong_count >= 1.0 else base_offset
        if mode == "voice_relaxed":
            return 0.0 if prev_strong_count >= 1.0 or market_voice_score >= 0.45 else base_offset
        if mode == "thin_coverage_relaxed":
            return 0.0 if prev_strong_count >= 1.0 and holding_count <= 2 else base_offset
        if mode == "two_stage":
            if prev_strong_count >= 1.0 and (market_voice_score >= 0.40 or state_transition_score >= 0.35):
                return 0.0
            if combined_add_readiness >= threshold + 0.02:
                return base_offset / 2.0
            return base_offset
        return base_offset

    def _simulate_with_candidate_audit(
        self,
        *,
        config: dict[str, Any],
        episode_rows: list[dict[str, Any]],
        board_symbols: set[str],
        daily_bars: dict[tuple[str, Any], dict[str, Any]],
    ) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
        symbol_map = {
            "packaging_process_enabler": "300757",
            "core_module_leader": "300308",
            "high_beta_core_module": "300502",
            "laser_chip_component": "688498",
        }
        family_by_symbol = {value: key for key, value in symbol_map.items()}
        episode_by_date: dict[Any, list[dict[str, Any]]] = {}
        for row in episode_rows:
            episode_by_date.setdefault(parse_trade_date(str(row["trade_date"])), []).append(row)

        min_episode_date = min(parse_trade_date(str(row["trade_date"])) for row in episode_rows)
        max_episode_date = max(parse_trade_date(str(row["trade_date"])) for row in episode_rows)
        trade_dates = sorted({trade_date for (_, trade_date) in daily_bars if min_episode_date <= trade_date <= max_episode_date})

        account_cash = 1_000_000.0
        positions_qty: dict[str, int] = {}
        positions_sellable_qty: dict[str, int] = {}
        positions_last_buy_date: dict[str, Any] = {}
        previous_equity = 1_000_000.0
        equity_peak = 1_000_000.0
        max_drawdown = 0.0
        executed_orders = 0
        under_exposure_penalty = 0.0
        audit_day_rows: list[dict[str, Any]] = []
        action_rows: list[dict[str, Any]] = []
        board_history: list[dict[str, Any]] = []
        base_floor = float(config["under_exposure_floor"])

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
            for symbol, qty in positions_qty.items():
                market_state = market_by_symbol.get(symbol)
                if market_state is not None:
                    market_value += qty * market_state.last_price

            equity = account_cash + market_value
            equity_peak = max(equity_peak, equity)
            max_drawdown = max(max_drawdown, 0.0 if equity_peak <= 0 else 1.0 - equity / equity_peak)
            board_context = self.base._build_board_context(
                trade_date=trade_date,
                board_symbols=board_symbols,
                daily_bars=daily_bars,
            )
            current_gross = 0.0 if equity <= 0 else market_value / equity
            holding_count = sum(1 for qty in positions_qty.values() if qty > 0)
            scores = self._compute_candidate_scores(
                board_context=board_context,
                previous_board_contexts=board_history,
                current_gross=current_gross,
                holding_count=holding_count,
                base_floor=base_floor,
            )
            board_strong = (
                float(board_context["avg_return"]) >= float(config["board_avg_return_min"])
                and float(board_context["breadth"]) >= float(config["board_breadth_min"])
            )
            candidate_add_band = (
                board_strong
                and float(scores["combined_add_readiness"]) >= float(config["candidate_add_threshold"])
                and holding_count >= 1
                and current_gross < float(config["candidate_floor"])
            )
            effective_uplift = float(config["strong_board_uplift"]) + (
                float(config["candidate_extra_uplift"]) if candidate_add_band else 0.0
            )
            effective_floor = max(base_floor, float(config["candidate_floor"]) if candidate_add_band else base_floor)
            if board_strong and current_gross < effective_floor:
                under_exposure_penalty += effective_floor - current_gross

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
                boosted_weight = min(float(config["max_expression_weight"]), base_weight + effective_uplift)
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
                                strategy_id="cpo_market_voice_transition_audit_replay",
                                source=f"{object_id}:{control_label}",
                                rationale="candidate_audit_target_weight_expression",
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
                                strategy_id="cpo_market_voice_transition_audit_replay",
                                source=f"{object_id}:{control_label}",
                                rationale="respect_derisk_band_from_default_surface",
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
                            strategy_id="cpo_market_voice_transition_audit_replay",
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
                    target_weight = min(float(config["max_expression_weight"]), base_weight + effective_uplift)
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
                                strategy_id="cpo_market_voice_transition_audit_replay",
                                source=f"{object_id}:candidate_add_band" if candidate_add_band else f"{object_id}:board_strength_add",
                                rationale="candidate_add_follow_through" if candidate_add_band else "board_strength_follow_through_add",
                                tags=(object_id, "eligibility", "candidate_audit" if candidate_add_band else "promoted_default", "add"),
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
                    add_confirmation_offset = self._resolve_add_confirmation_offset(
                        config=config,
                        scores=scores,
                        holding_count=holding_count,
                    )
                    if current_qty > 0 and float(scores["combined_add_readiness"]) < float(config["candidate_add_threshold"]) + add_confirmation_offset:
                        continue
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
                    max_order_notional = float(config.get("max_order_notional", 300_000.0))
                    max_order_qty = self.base._lot_round(max_order_notional, market_state.last_price)
                    max_weight_qty = self.base._lot_round(max(0.0, float(config["max_expression_weight"]) * equity - current_value), market_state.last_price)
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
                            "candidate_add_band": candidate_add_band,
                            "combined_add_readiness": scores["combined_add_readiness"],
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
                    "candidate_add_band": candidate_add_band,
                    "market_voice_score": scores["market_voice_score"],
                    "state_transition_score": scores["state_transition_score"],
                    "combined_add_readiness": scores["combined_add_readiness"],
                    "effective_floor": round(effective_floor, 6),
                    "effective_uplift": round(effective_uplift, 6),
                    "equity_after_close": round(equity_after, 4),
                    "gross_exposure_after_close": round(gross_exposure_after, 6),
                    "action_count": executed_today,
                    "action_mode_counts": action_mode_counts,
                    "holding_symbols_after_close": sorted(holdings_after),
                }
            )
            board_history.append(board_context)

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
        v114h_payload: dict[str, Any],
        v114j_payload: dict[str, Any],
    ) -> V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayReport:
        summary_n = dict(v113n_payload.get("summary", {}))
        summary_v = dict(v113v_payload.get("summary", {}))
        summary_e = dict(v114e_payload.get("summary", {}))
        summary_h = dict(v114h_payload.get("summary", {}))
        summary_j = dict(v114j_payload.get("summary", {}))
        if str(summary_n.get("acceptance_posture")) != "freeze_v113n_cpo_real_board_episode_population_v1":
            raise ValueError("V1.14K expects V1.13N real board episode population.")
        if str(summary_v.get("acceptance_posture")) != "freeze_v113v_cpo_full_board_execution_main_feed_replay_v1":
            raise ValueError("V1.14K expects V1.13V full-board replay.")
        if str(summary_e.get("acceptance_posture")) != "freeze_v114e_cpo_default_sizing_replay_promotion_v1":
            raise ValueError("V1.14K expects V1.14E default sizing replay promotion.")
        if str(summary_h.get("acceptance_posture")) != "freeze_v114h_cpo_promoted_sizing_behavior_audit_v1":
            raise ValueError("V1.14K expects V1.14H promoted sizing behavior audit.")
        if str(summary_j.get("acceptance_posture")) != "freeze_v114j_cpo_market_voice_state_transition_vector_prototype_v1":
            raise ValueError("V1.14K expects V1.14J vector prototype.")

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
        candidate_config = dict(promoted_config)
        candidate_config.update(
            {
                "candidate_add_threshold": round(float(v114j_payload.get("prototype_summary", {}).get("market_voice_add_threshold", 0.35)), 6),
                "candidate_extra_uplift": 0.02,
                "candidate_floor": 0.35,
                "max_expression_weight": 0.14,
            }
        )
        candidate_summary_row, candidate_day_rows, candidate_action_rows = self._simulate_with_candidate_audit(
            config=candidate_config,
            episode_rows=episode_rows,
            board_symbols=board_symbols,
            daily_bars=daily_bars,
        )

        promoted_reference_map = {str(row["trade_date"]): row for row in list(v114h_payload.get("remaining_under_exposed_rows", []))}
        baseline_day_map = {str(row["trade_date"]): row for row in list(v113v_payload.get("replay_day_rows", []))}
        base_floor = float(promoted_config["under_exposure_floor"])

        strong_board_days = 0
        candidate_add_band_days = 0
        newly_improved_rows: list[dict[str, Any]] = []
        remaining_under_exposed_rows: list[dict[str, Any]] = []
        for row in candidate_day_rows:
            if not bool(row["board_strong"]):
                continue
            strong_board_days += 1
            trade_date = str(row["trade_date"])
            if bool(row["candidate_add_band"]):
                candidate_add_band_days += 1
            baseline_row = baseline_day_map.get(trade_date)
            baseline_exposure = float(baseline_row["gross_exposure_after_close"]) if baseline_row is not None else 0.0
            candidate_exposure = float(row["gross_exposure_after_close"])
            promoted_ref = promoted_reference_map.get(trade_date)
            if promoted_ref is not None:
                promoted_exposure = float(promoted_ref["promoted_exposure"])
                if candidate_exposure - promoted_exposure > 0.03:
                    newly_improved_rows.append(
                        {
                            "trade_date": trade_date,
                            "board_avg_return": round(float(row["board_avg_return"]), 6),
                            "board_breadth": round(float(row["board_breadth"]), 6),
                            "baseline_exposure": round(baseline_exposure, 6),
                            "promoted_exposure": round(promoted_exposure, 6),
                            "candidate_exposure": round(candidate_exposure, 6),
                            "candidate_delta_vs_promoted": round(candidate_exposure - promoted_exposure, 6),
                            "candidate_add_band": bool(row["candidate_add_band"]),
                            "combined_add_readiness": float(row["combined_add_readiness"]),
                            "holding_symbols_after_close": list(row["holding_symbols_after_close"]),
                        }
                    )
            if candidate_exposure < base_floor:
                remaining_under_exposed_rows.append(
                    {
                        "trade_date": trade_date,
                        "board_avg_return": round(float(row["board_avg_return"]), 6),
                        "board_breadth": round(float(row["board_breadth"]), 6),
                        "candidate_exposure": round(candidate_exposure, 6),
                        "under_exposure_gap": round(base_floor - candidate_exposure, 6),
                        "candidate_add_band": bool(row["candidate_add_band"]),
                        "combined_add_readiness": float(row["combined_add_readiness"]),
                        "holding_symbols_after_close": list(row["holding_symbols_after_close"]),
                    }
                )

        top_newly_improved_rows = sorted(
            newly_improved_rows,
            key=lambda item: (item["candidate_delta_vs_promoted"], item["board_avg_return"]),
            reverse=True,
        )[:10]
        remaining_under_exposed_rows = sorted(
            remaining_under_exposed_rows,
            key=lambda item: (item["under_exposure_gap"], item["board_avg_return"]),
            reverse=True,
        )[:10]

        promoted_remaining = int(summary_h.get("remaining_under_exposed_strong_day_count", 0))
        candidate_remaining = sum(
            1 for row in candidate_day_rows if bool(row["board_strong"]) and float(row["gross_exposure_after_close"]) < base_floor
        )

        candidate_policy_summary = {
            "strong_board_day_count": strong_board_days,
            "candidate_add_band_days": candidate_add_band_days,
            "newly_improved_expression_day_count": len(newly_improved_rows),
            "promoted_remaining_under_exposed_count": promoted_remaining,
            "candidate_remaining_under_exposed_count": candidate_remaining,
            "candidate_action_count": len(candidate_action_rows),
            "candidate_add_action_count": len([row for row in candidate_action_rows if row["action_mode"] == "add"]),
            "candidate_reduce_action_count": len([row for row in candidate_action_rows if row["action_mode"] == "reduce"]),
            "candidate_add_threshold": round(float(candidate_config["candidate_add_threshold"]), 6),
            "candidate_extra_uplift": round(float(candidate_config["candidate_extra_uplift"]), 6),
            "candidate_floor": round(float(candidate_config["candidate_floor"]), 6),
            "candidate_max_expression_weight": round(float(candidate_config["max_expression_weight"]), 6),
        }

        summary = {
            "acceptance_posture": "freeze_v114k_cpo_market_voice_state_transition_add_reduce_audit_replay_v1",
            "promoted_curve": round(float(summary_h.get("promoted_curve", 0.0)), 4),
            "candidate_curve": round(float(candidate_summary_row["final_curve"]), 4),
            "promoted_max_drawdown": round(float(summary_h.get("promoted_max_drawdown", 0.0)), 4),
            "candidate_max_drawdown": round(float(candidate_summary_row["max_drawdown"]), 4),
            "curve_delta_vs_promoted": round(float(candidate_summary_row["final_curve"]) - float(summary_h.get("promoted_curve", 0.0)), 4),
            "drawdown_delta_vs_promoted": round(float(candidate_summary_row["max_drawdown"]) - float(summary_h.get("promoted_max_drawdown", 0.0)), 4),
            "candidate_add_band_days": candidate_add_band_days,
            "remaining_under_exposed_reduction": promoted_remaining - candidate_remaining,
            "recommended_next_posture": "use_v114k_candidate_add_reduce_audit_to_decide_if_market_voice_and_state_transition_scores_deserve_candidate_binding",
        }
        interpretation = [
            "V1.14K does not let market-voice and state-transition scores legislate new symbols. It only uses them as a candidate add-band overlay on top of the promoted default sizing surface.",
            "The audit question is narrow: can candidate scores reduce the remaining under-expressed strong-board days by accelerating adds on already-mature holdings?",
            "This keeps hard vetoes intact and treats the vector scores as a replay-judged candidate layer rather than a new source of law.",
        ]

        return V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayReport(
            summary=summary,
            candidate_policy_summary=candidate_policy_summary,
            top_newly_improved_rows=top_newly_improved_rows,
            remaining_under_exposed_rows=remaining_under_exposed_rows,
            candidate_action_rows=candidate_action_rows,
            interpretation=interpretation,
        )


def write_v114k_cpo_market_voice_state_transition_add_reduce_audit_replay_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
