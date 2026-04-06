from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kj_a_share_ki_quality_direction_triage_v1 import (
    V134KJAShareKIQualityDirectionTriageV1Analyzer,
)


def test_v134kj_quality_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KJAShareKIQualityDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["materialized_source_quality_count"] == 36
    assert report.summary["materialized_event_quality_count"] == 52
    assert (
        report.summary["authoritative_status"]
        == "quality_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_attention_with_quality_guardrails"
    )


def test_v134kj_quality_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KJAShareKIQualityDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["quality_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == "move_into_attention_layer_using_quality_registry_as_guardrail_input"
