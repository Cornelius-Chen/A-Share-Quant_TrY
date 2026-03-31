from __future__ import annotations

from a_share_quant.strategy.v112a_price_cycle_inference_v2 import (
    V112APriceCycleInferenceV2Analyzer,
)


def test_v2_includes_300308_unified_window() -> None:
    analyzer = V112APriceCycleInferenceV2Analyzer()
    assert analyzer.SUGGESTED_WINDOWS["300308"]["first_markup_start"] == "2023-02"
    assert analyzer.SUGGESTED_WINDOWS["300308"]["major_markup_start"] == "2025-06"


def test_v2_notes_cover_reinferred_anchor() -> None:
    analyzer = V112APriceCycleInferenceV2Analyzer()
    assert "统一价格结构口径" in analyzer._notes_for_symbol("300308")
