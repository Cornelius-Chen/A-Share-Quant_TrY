from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134rl_a_share_rk_internal_hot_news_ingress_direction_triage_v1 import (
    V134RLAShareRKInternalHotNewsIngressDirectionTriageV1Analyzer,
)


def test_v134rl_ingress_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RLAShareRKInternalHotNewsIngressDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["ingress_row_count"] > 0


def test_v134rl_ingress_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134RLAShareRKInternalHotNewsIngressDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "single_ingress_surface" in rows["consumer_entry"]
    assert "program_priority_score" in rows["priority_ordering"]
    assert "hot_window_state" in rows["retention_awareness"]
    assert "impact_window_state" in rows["context_awareness"]
    assert "context_recency_weighted_signal" in rows["context_awareness"]
