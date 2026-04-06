from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ks_a_share_kr_pti_direction_triage_v1 import (
    V134KSAShareKRPTIDirectionTriageV1Analyzer,
)


def test_v134ks_pti_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KSAShareKRPTIDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["event_ledger_count"] == 52
    assert report.summary["time_slice_count"] > 0
    assert (
        report.summary["authoritative_status"]
        == "pti_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_replay_population"
    )


def test_v134ks_pti_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KSAShareKRPTIDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["pti_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == "move_into_replay_workstream_using_bootstrap_pti_surfaces_as_input"
