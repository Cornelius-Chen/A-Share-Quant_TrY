from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kw_a_share_kv_replay_direction_triage_v1 import (
    V134KWAShareKVReplayDirectionTriageV1Analyzer,
)


def test_v134kw_replay_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KWAShareKVReplayDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["shadow_surface_row_count"] == 17
    assert (
        report.summary["authoritative_status"]
        == "replay_workstream_complete_enough_to_freeze_as_read_only_shadow_and_shift_into_serving"
    )


def test_v134kw_replay_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KWAShareKVReplayDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["replay_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == (
        "shift_into_serving_workstream_using_identity_events_market_features_pti_and_replay_as_inputs"
    )
