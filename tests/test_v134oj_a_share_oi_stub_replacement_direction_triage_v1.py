from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134oj_a_share_oi_stub_replacement_direction_triage_v1 import (
    V134OJAShareOIStubReplacementDirectionTriageV1Analyzer,
)


def test_v134oj_stub_replacement_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OJAShareOIStubReplacementDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "shadow_execution_stub_should_remain_until_market_context_closes_despite_replay_foundation_progress"
    )


def test_v134oj_stub_replacement_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OJAShareOIStubReplacementDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["market_context"]["direction"].startswith("treat_market_context_closure")
    assert rows["paired_surface_promotion"]["direction"].startswith("treat_daily_market_promotion_and_pairing")
