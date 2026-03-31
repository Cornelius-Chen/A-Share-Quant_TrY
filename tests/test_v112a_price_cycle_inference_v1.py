from __future__ import annotations

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import (
    V112APriceCycleInferenceAnalyzer,
)


def test_notes_for_symbol_contains_expected_phrase() -> None:
    analyzer = V112APriceCycleInferenceAnalyzer()
    assert "第一轮主升" in analyzer._notes_for_symbol("300502")
    assert "最新主升段" in analyzer._notes_for_symbol("300394")


def test_suggested_windows_cover_two_pending_symbols() -> None:
    analyzer = V112APriceCycleInferenceAnalyzer()
    assert set(analyzer.SUGGESTED_WINDOWS) == {"300502", "300394"}
    assert analyzer.SUGGESTED_WINDOWS["300502"]["major_markup_start"] == "2025-06"
