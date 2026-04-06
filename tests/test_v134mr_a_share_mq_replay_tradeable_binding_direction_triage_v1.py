from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mr_a_share_mq_replay_tradeable_binding_direction_triage_v1 import (
    V134MRAShareMQReplayTradeableBindingDirectionTriageV1Analyzer,
)


def test_v134mr_replay_tradeable_binding_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MRAShareMQReplayTradeableBindingDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "replay_tradeable_context_bound_at_date_level_but_not_symbol_level"
    )


def test_v134mr_replay_tradeable_binding_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MRAShareMQReplayTradeableBindingDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["tradeable_context_binding"]["direction"].startswith("freeze_date_level_binding")
