from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134rd_a_share_rc_internal_hot_news_guidance_direction_triage_v1 import (
    V134RDAShareRCInternalHotNewsGuidanceDirectionTriageV1Analyzer,
)


def test_v134rd_internal_hot_news_guidance_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RDAShareRCInternalHotNewsGuidanceDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["guidance_row_count"] > 0


def test_v134rd_internal_hot_news_guidance_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RDAShareRCInternalHotNewsGuidanceDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "structured_guidance_fields" in rows["message_normalization"]
    assert "guidance_surface" in rows["trading_delivery"]
    assert "market_guidance_view" in rows["market_guidance_delivery"]
    assert "risk_queue_view" in rows["risk_queue_delivery"]
    assert "board_signal_view" in rows["board_signal_delivery"]
    assert "decision_signal_view" in rows["decision_signal_delivery"]
