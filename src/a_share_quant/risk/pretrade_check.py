from __future__ import annotations

from math import floor
from pathlib import Path
from typing import Any

import yaml

from a_share_quant.execution.models import (
    AccountSnapshot,
    ExecutionIntent,
    PositionSnapshot,
    PretradeDecision,
    SymbolMarketState,
)


class PretradeChecker:
    """Minimal rule-based pretrade gate using the repo risk policy file."""

    def __init__(self, *, risk_limits_path: Path) -> None:
        with risk_limits_path.open("r", encoding="utf-8") as handle:
            self.config = yaml.safe_load(handle)

    def evaluate(
        self,
        *,
        intent: ExecutionIntent,
        account: AccountSnapshot,
        position: PositionSnapshot | None,
        market_state: SymbolMarketState,
    ) -> PretradeDecision:
        reasons: list[str] = []
        observed: dict[str, Any] = {
            "cash": account.cash,
            "equity": account.equity,
            "last_price": market_state.last_price,
        }

        fail_safe = dict(self.config.get("fail_safe", {}))
        if fail_safe.get("reject_if_market_data_stale") and account.market_data_age_ms > int(fail_safe.get("market_data_stale_ms", 0)):
            reasons.append("market_data_stale")
        if fail_safe.get("reject_if_position_snapshot_stale") and account.position_snapshot_age_sec > int(fail_safe.get("position_snapshot_stale_sec", 0)):
            reasons.append("position_snapshot_stale")
        if fail_safe.get("reject_if_risk_engine_unavailable") and not account.risk_engine_available:
            reasons.append("risk_engine_unavailable")
        if fail_safe.get("reject_if_broker_ack_timeout") and not account.broker_ack_healthy:
            reasons.append("broker_ack_unhealthy")

        state_limits = dict(self.config.get("special_state_limits", {}))
        if state_limits.get("block_if_suspended") and market_state.is_suspended:
            reasons.append("symbol_suspended")
        if state_limits.get("block_if_st") and market_state.is_st:
            reasons.append("symbol_st")
        if state_limits.get("block_if_limit_up") and market_state.is_limit_up and intent.action == "buy":
            reasons.append("limit_up_buy_block")
        if state_limits.get("block_if_limit_down") and market_state.is_limit_down and intent.action == "sell":
            reasons.append("limit_down_sell_block")
        if state_limits.get("block_if_near_limit_up") and market_state.is_near_limit_up and intent.action == "buy":
            reasons.append("near_limit_up_buy_block")
        if state_limits.get("block_if_near_limit_down") and market_state.is_near_limit_down and intent.action == "sell":
            reasons.append("near_limit_down_sell_block")
        if market_state.listed_days < int(state_limits.get("block_if_new_listing_within_n_days", 0)):
            reasons.append("new_listing_block")

        liquidity = dict(self.config.get("liquidity_limits", {}))
        if market_state.turnover < float(liquidity.get("min_turnover_threshold", 0.0)):
            reasons.append("turnover_below_threshold")
        observed["market_cap_reliable"] = bool(market_state.market_cap_reliable)
        if market_state.market_cap_reliable and market_state.market_cap < float(liquidity.get("min_market_cap_threshold", 0.0)):
            reasons.append("market_cap_below_threshold")
        if market_state.last_price < float(liquidity.get("min_price_threshold", 0.0)):
            reasons.append("price_below_threshold")

        volatility = dict(self.config.get("volatility_limits", {}))
        if intent.action == "buy":
            if market_state.gap_up_pct > float(volatility.get("max_gap_up_allowed_for_new_buy", 1.0)):
                reasons.append("gap_up_too_large")
            if market_state.gap_down_pct > float(volatility.get("max_gap_down_allowed_for_new_buy", 1.0)):
                reasons.append("gap_down_too_large")
        if market_state.intraday_volatility > float(volatility.get("max_intraday_volatility_allowed", 1.0)):
            reasons.append("intraday_volatility_too_large")

        order_limits = dict(self.config.get("order_limits", {}))
        requested_qty = max(0, int(intent.quantity))
        max_order_value = float(order_limits.get("max_order_value", 0.0) or 0.0)
        min_order_value = float(order_limits.get("min_order_value", 0.0) or 0.0)
        max_order_qty = int(order_limits.get("max_order_qty", 0) or 0)
        if requested_qty <= 0:
            reasons.append("non_positive_quantity")
            adjusted_qty = 0
        else:
            adjusted_qty = requested_qty
            if max_order_value > 0.0:
                adjusted_qty = min(adjusted_qty, floor(max_order_value / market_state.last_price))
            if max_order_qty > 0:
                adjusted_qty = min(adjusted_qty, max_order_qty)

        symbol_limits = dict(self.config.get("symbol_limits", {}))
        if intent.action == "buy":
            account_limit_qty = None
            if account.equity > 0.0:
                max_account_weight = float(symbol_limits.get("max_position_pct_of_account", 1.0))
                account_limit_qty = floor(account.equity * max_account_weight / market_state.last_price)
            strategy_limit_qty = None
            if account.equity > 0.0:
                max_strategy_weight = float(symbol_limits.get("max_position_pct_of_strategy", 1.0))
                strategy_limit_qty = floor(account.equity * max_strategy_weight / market_state.last_price)
            if account_limit_qty is not None:
                adjusted_qty = min(adjusted_qty, max(0, account_limit_qty - int(position.quantity if position else 0)))
            if strategy_limit_qty is not None:
                adjusted_qty = min(adjusted_qty, max(0, strategy_limit_qty - int(position.quantity if position else 0)))
            max_position_value = float(symbol_limits.get("max_position_value", 0.0) or 0.0)
            if max_position_value > 0.0:
                current_value = float(position.market_value if position else 0.0)
                value_headroom = max(0.0, max_position_value - current_value)
                adjusted_qty = min(adjusted_qty, floor(value_headroom / market_state.last_price))
        else:
            current_qty = int(position.quantity if position else 0)
            sellable_qty = int(position.sellable_quantity) if position and position.sellable_quantity is not None else current_qty
            adjusted_qty = min(adjusted_qty, sellable_qty)
            observed["sellable_quantity"] = sellable_qty
            if position and position.last_buy_trade_date == intent.trade_date and sellable_qty <= 0:
                reasons.append("t_plus_one_sell_block")

        if position is not None:
            if position.add_count_today >= int(symbol_limits.get("max_add_count_per_day", 999999)) and intent.action == "buy":
                reasons.append("max_add_count_reached")
            if position.order_count_today >= int(symbol_limits.get("max_order_count_per_symbol_per_day", 999999)):
                reasons.append("max_order_count_reached")

        notional = adjusted_qty * market_state.last_price
        observed["adjusted_notional"] = round(notional, 4)
        account_limits = dict(self.config.get("account_limits", {}))
        strategy_limits = dict(self.config.get("strategy_limits", {}))
        if account.equity > 0.0 and intent.action == "buy":
            projected_cash_usage = account.gross_exposure + (notional / account.equity)
            observed["projected_cash_usage"] = round(projected_cash_usage, 6)
            max_cash_usage = float(account_limits.get("max_cash_usage", 1.0))
            if projected_cash_usage > max_cash_usage:
                reasons.append("max_cash_usage_exceeded")
            projected_day_turnover = account.daily_turnover + notional
            observed["projected_day_turnover_pct"] = round(projected_day_turnover / account.equity, 6)
            max_single_day_turnover = float(account_limits.get("max_single_day_turnover", 999999.0))
            if projected_day_turnover / account.equity > max_single_day_turnover:
                reasons.append("max_single_day_turnover_exceeded")
            max_strategy_turnover = float(strategy_limits.get("max_strategy_turnover_per_day", 999999.0))
            if projected_day_turnover / account.equity > max_strategy_turnover:
                reasons.append("max_strategy_turnover_exceeded")
            max_strategy_gross = float(strategy_limits.get("max_strategy_gross_exposure", 1.0))
            if projected_cash_usage > max_strategy_gross:
                reasons.append("max_strategy_gross_exposure_exceeded")

        max_pct_of_adv_5d = float(liquidity.get("max_pct_of_adv_5d", 1.0))
        max_pct_of_adv_20d = float(liquidity.get("max_pct_of_adv_20d", 1.0))
        if market_state.adv_5d > 0 and notional / market_state.adv_5d > max_pct_of_adv_5d:
            reasons.append("max_pct_of_adv_5d_exceeded")
        if market_state.adv_20d > 0 and notional / market_state.adv_20d > max_pct_of_adv_20d:
            reasons.append("max_pct_of_adv_20d_exceeded")

        if adjusted_qty <= 0:
            reasons.append("quantity_reduced_to_zero")
        elif notional < min_order_value:
            reasons.append("order_value_below_minimum")
            adjusted_qty = 0

        if intent.action == "buy" and notional > account.cash:
            affordable_qty = floor(account.cash / market_state.last_price)
            adjusted_qty = min(adjusted_qty, max(0, affordable_qty))
            observed["cash_capped_quantity"] = adjusted_qty
            if adjusted_qty <= 0:
                reasons.append("insufficient_cash")

        approved = len(reasons) == 0
        return PretradeDecision(
            approved=approved,
            adjusted_quantity=int(adjusted_qty),
            reasons=tuple(reasons),
            observed=observed,
        )
