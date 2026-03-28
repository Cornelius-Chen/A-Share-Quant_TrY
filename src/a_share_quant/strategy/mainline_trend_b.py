from __future__ import annotations

from a_share_quant.strategy.mainline_strategy_base import BaseMainlineTrendStrategy


class MainlineTrendB(BaseMainlineTrendStrategy):
    strategy_name = "mainline_trend_b"
    allowed_layers = ("leader", "core")
