from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mt_a_share_ms_replay_market_coverage_direction_triage_v1 import (
    V134MTAShareMSReplayMarketCoverageDirectionTriageV1Analyzer,
)


def test_v134mt_replay_market_coverage_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MTAShareMSReplayMarketCoverageDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "replay_market_coverage_gap_narrowed_to_residual_missing_date_contexts"
    )


def test_v134mt_replay_market_coverage_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MTAShareMSReplayMarketCoverageDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}
    assert rows["daily_market_coverage"]["direction"].startswith("close_only_the_residual_missing_date_contexts")
