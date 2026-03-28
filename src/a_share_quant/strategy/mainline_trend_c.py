from __future__ import annotations

from a_share_quant.strategy.mainline_strategy_base import BaseMainlineTrendStrategy


class MainlineTrendC(BaseMainlineTrendStrategy):
    strategy_name = "mainline_trend_c"
    allowed_layers = ("leader", "core", "late_mover")
