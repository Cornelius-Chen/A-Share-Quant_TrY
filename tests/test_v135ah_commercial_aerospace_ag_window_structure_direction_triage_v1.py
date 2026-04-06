from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ah_commercial_aerospace_ag_window_structure_direction_triage_v1 import (
    V135AHCommercialAerospaceAGWindowStructureDirectionTriageV1Analyzer,
)


def test_v135ah_window_structure_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AHCommercialAerospaceAGWindowStructureDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["window_count"] == 3
    assert report.summary["ready_negative_sample_count"] == 1
    assert report.summary["policy_hold_count"] == 1
    assert report.summary["partial_subwindow_count"] == 1


def test_v135ah_window_structure_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AHCommercialAerospaceAGWindowStructureDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) == 3
    recommendations = {row["sample_window_id"]: row["recommendation"] for row in report.triage_rows}
    assert recommendations["ca_train_window_002"] == "keep_window_off_final_training_until_january_policy_text_is_locked"
    assert recommendations["ca_train_window_008"] == "allow_subwindow_learning_only_and_continue_february_followthrough_backfill"
    assert recommendations["ca_train_window_010"] == "allow_negative_sample_training_and_keep_launch_chain_expansion_under_review"
