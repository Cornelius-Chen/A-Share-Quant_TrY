from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ae_a_share_internal_hot_news_incumbent_vs_challenger_rotation_review_audit_v1 import (
    V135AEAShareInternalHotNewsIncumbentVsChallengerRotationReviewAuditV1Analyzer,
)


def test_v135ae_incumbent_vs_challenger_review_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AEAShareInternalHotNewsIncumbentVsChallengerRotationReviewAuditV1Analyzer(repo_root).analyze()

    assert report.summary["incumbent_theme_slug"] not in {"", "none"}
    assert report.summary["incumbent_watch_symbol"]
    assert report.summary["challenger_theme_slug"] not in {"", "none", report.summary["incumbent_theme_slug"]}
    assert report.summary["challenger_watch_symbol"] != report.summary["incumbent_watch_symbol"]


def test_v135ae_incumbent_vs_challenger_review_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AEAShareInternalHotNewsIncumbentVsChallengerRotationReviewAuditV1Analyzer(repo_root).analyze()
    rows = {row["metric"]: row["value"] for row in report.rows}

    assert rows["review_state"] in {
        "hold_incumbent_focus",
        "keep_incumbent_but_raise_review_attention",
        "open_next_rotation_review",
    }
