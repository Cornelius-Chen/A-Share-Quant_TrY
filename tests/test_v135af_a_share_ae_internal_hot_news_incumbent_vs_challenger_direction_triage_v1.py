from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135af_a_share_ae_internal_hot_news_incumbent_vs_challenger_direction_triage_v1 import (
    V135AFAShareAEInternalHotNewsIncumbentVsChallengerDirectionTriageV1Analyzer,
)


def test_v135af_incumbent_vs_challenger_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AFAShareAEInternalHotNewsIncumbentVsChallengerDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["incumbent_theme_slug"] not in {"", "none"}
    assert report.summary["challenger_theme_slug"] not in {"", "none", report.summary["incumbent_theme_slug"]}
    assert report.summary["review_state"] in {
        "hold_incumbent_focus",
        "keep_incumbent_but_raise_review_attention",
        "open_next_rotation_review",
    }


def test_v135af_incumbent_vs_challenger_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AFAShareAEInternalHotNewsIncumbentVsChallengerDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
