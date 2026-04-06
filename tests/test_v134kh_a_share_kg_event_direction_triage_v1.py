from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kh_a_share_kg_event_direction_triage_v1 import (
    V134KHAShareKGEventDirectionTriageV1Analyzer,
)


def test_v134kh_event_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KHAShareKGEventDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["materialized_event_count"] == 52
    assert (
        report.summary["authoritative_status"]
        == "event_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_quality_and_pti_enrichment"
    )


def test_v134kh_event_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KHAShareKGEventDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["event_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == "move_into_quality_layer_and_point_in_time_enrichment_using_bootstrapped_event_chain_as_input"
