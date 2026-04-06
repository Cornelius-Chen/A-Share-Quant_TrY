from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ko_a_share_kn_label_direction_triage_v1 import (
    V134KOAShareKNLabelDirectionTriageV1Analyzer,
)


def test_v134ko_label_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KOAShareKNLabelDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["label_definition_count"] == 15
    assert report.summary["label_assignment_count"] == 58
    assert (
        report.summary["authoritative_status"]
        == "label_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_feature_registry_population"
    )


def test_v134ko_label_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KOAShareKNLabelDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["label_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == "move_into_feature_registry_population_using_central_label_registry_as_input"
