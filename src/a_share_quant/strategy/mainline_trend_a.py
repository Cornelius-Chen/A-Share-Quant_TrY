from __future__ import annotations

from a_share_quant.strategy.mainline_strategy_base import BaseMainlineTrendStrategy


class MainlineTrendA(BaseMainlineTrendStrategy):
    strategy_name = "mainline_trend_a"
    allowed_layers = ("leader",)
