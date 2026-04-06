from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ku_a_share_kt_market_direction_triage_v1 import (
    V134KUAShareKTMarketDirectionTriageV1Analyzer,
)


def test_v134ku_market_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KUAShareKTMarketDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["daily_symbol_count"] == 8
    assert report.summary["intraday_trade_date_count"] == 102
    assert (
        report.summary["authoritative_status"]
        == "market_workstream_complete_enough_to_freeze_as_storage_aware_foundation_and_shift_into_replay"
    )


def test_v134ku_market_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KUAShareKTMarketDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["market_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == (
        "shift_into_replay_with_market_foundation_as_input_and_leave_board_state_derivation_explicitly_backlogged"
    )
