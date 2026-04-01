from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from a_share_quant.execution.models import AccountSnapshot, ExecutionIntent, RiskDecision


class RiskEngine:
    """Minimal account/strategy gate with size reduction and block postures."""

    def __init__(self, *, risk_limits_path: Path) -> None:
        with risk_limits_path.open("r", encoding="utf-8") as handle:
            self.config = yaml.safe_load(handle)

    def evaluate(
        self,
        *,
        intent: ExecutionIntent,
        account: AccountSnapshot,
    ) -> RiskDecision:
        reasons: list[str] = []
        posture = "allow"
        size_multiplier = 1.0
        observed: dict[str, Any] = {
            "daily_loss_pct": account.daily_loss_pct,
            "gross_exposure": account.gross_exposure,
            "net_exposure": account.net_exposure,
            "open_order_count": account.open_order_count,
            "open_position_count": account.open_position_count,
        }

        if account.strategy_halted:
            reasons.append("strategy_halted")
            return RiskDecision(False, 0.0, "strategy_halt", tuple(reasons), observed)

        if account.reduce_only_mode and intent.action == "buy":
            reasons.append("reduce_only_mode")
            return RiskDecision(False, 0.0, "reduce_only", tuple(reasons), observed)

        account_limits = dict(self.config.get("account_limits", {}))
        if account.gross_exposure >= float(account_limits.get("max_gross_exposure", 1.0)):
            reasons.append("gross_exposure_limit")
        if abs(account.net_exposure) >= float(account_limits.get("max_net_exposure", 1.0)):
            reasons.append("net_exposure_limit")
        if account.open_order_count >= int(account_limits.get("max_total_open_orders", 999999)):
            reasons.append("open_order_limit")
        if account.open_position_count >= int(account_limits.get("max_total_open_positions", 999999)) and intent.action == "buy":
            reasons.append("open_position_limit")

        threshold_actions = dict(self.config.get("threshold_actions", {}))
        hard_stop = dict(threshold_actions.get("hard_stop_threshold", {}))
        warning2 = dict(threshold_actions.get("warning_threshold_2", {}))
        warning1 = dict(threshold_actions.get("warning_threshold_1", {}))

        if account.daily_loss_pct >= float(hard_stop.get("pnl_loss_pct", 1.0)):
            reasons.append("hard_stop_daily_loss")
            return RiskDecision(False, 0.0, "strategy_halt", tuple(reasons), observed)

        if account.daily_loss_pct >= float(warning2.get("pnl_loss_pct", 1.0)):
            posture = "block_new_positions"
            if intent.action == "buy":
                reasons.append("warning_threshold_2_block_new_positions")
                return RiskDecision(False, 0.0, posture, tuple(reasons), observed)

        if account.daily_loss_pct >= float(warning1.get("pnl_loss_pct", 1.0)):
            posture = "reduce_size"
            size_multiplier = min(size_multiplier, 0.5)
            reasons.append("warning_threshold_1_reduce_order_size")

        strategy_perf = dict(self.config.get("strategy_performance_limits", {}))
        if account.strategy_drawdown_pct >= float(strategy_perf.get("max_strategy_intraday_drawdown_pct", 1.0)):
            posture = "de_risk"
            size_multiplier = min(size_multiplier, 0.5)
            reasons.append("strategy_intraday_drawdown_limit")
        if account.account_drawdown_pct >= float(self.config.get("loss_limits", {}).get("max_account_drawdown_pct", 1.0)):
            reasons.append("account_drawdown_limit")
            return RiskDecision(False, 0.0, "account_halt", tuple(reasons), observed)

        allowed = len([r for r in reasons if r in {"gross_exposure_limit", "net_exposure_limit", "open_order_limit", "open_position_limit"}]) == 0
        if not allowed:
            return RiskDecision(False, 0.0, "block", tuple(reasons), observed)
        return RiskDecision(True, float(size_multiplier), posture, tuple(reasons), observed)
