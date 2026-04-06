from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kq_a_share_kp_feature_direction_triage_v1 import (
    V134KQAShareKPFeatureDirectionTriageV1Analyzer,
)


def test_v134kq_feature_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KQAShareKPFeatureDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["feature_registry_count"] == 9
    assert report.summary["feature_surface_row_count"] == 566
    assert (
        report.summary["authoritative_status"]
        == "feature_workstream_complete_enough_to_freeze_as_bootstrap_and_shift_into_pti_population"
    )


def test_v134kq_feature_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KQAShareKPFeatureDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["feature_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == "move_into_pti_workstream_using_central_feature_surface_and_label_registry_as_input"
