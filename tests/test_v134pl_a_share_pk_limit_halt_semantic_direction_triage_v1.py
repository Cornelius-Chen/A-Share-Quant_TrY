from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pl_a_share_pk_limit_halt_semantic_direction_triage_v1 import (
    V134PLASharePKLimitHaltSemanticDirectionTriageV1Analyzer,
)


def test_v134pl_limit_halt_semantic_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PLASharePKLimitHaltSemanticDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "limit_halt_semantic_surface_materialized_for_replay_recheck"
    )


def test_v134pl_limit_halt_semantic_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PLASharePKLimitHaltSemanticDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["promotion_review"]["direction"].startswith("rerun_daily_market_promotion_review_against_the_semantic_surface")
