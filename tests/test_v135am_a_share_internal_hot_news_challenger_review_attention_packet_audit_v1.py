from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135am_a_share_internal_hot_news_challenger_review_attention_packet_audit_v1 import (
    V135AMAShareInternalHotNewsChallengerReviewAttentionPacketAuditV1Analyzer,
)


def test_v135am_challenger_review_attention_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AMAShareInternalHotNewsChallengerReviewAttentionPacketAuditV1Analyzer(repo_root).analyze()

    assert report.summary["packet_row_count"] == 1
    assert report.summary["incumbent_theme_slug"] not in {"", "none"}
    assert report.summary["challenger_theme_slug"] not in {"", "none", report.summary["incumbent_theme_slug"]}
    assert report.summary["attention_state"] in {
        "open_rotation_review_now",
        "raise_review_attention_hold_incumbent",
        "background_monitor_only",
    }
    assert report.summary["attention_priority"] in {"p1", "p2", "p3"}


def test_v135am_challenger_review_attention_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AMAShareInternalHotNewsChallengerReviewAttentionPacketAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert rows["review_state"] in {
        "hold_incumbent_focus",
        "keep_incumbent_but_raise_review_attention",
        "open_next_rotation_review",
    }
    assert rows["attention_priority"] in {"p1", "p2", "p3"}
