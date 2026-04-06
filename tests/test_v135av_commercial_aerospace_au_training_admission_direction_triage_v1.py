from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135av_commercial_aerospace_au_training_admission_direction_triage_v1 import (
    V135AVCommercialAerospaceAUTrainingAdmissionDirectionTriageV1Analyzer,
)


def test_v135av_training_admission_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AVCommercialAerospaceAUTrainingAdmissionDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["window_count"] == 10
    assert result.summary["released_count"] == 9
    assert result.summary["hold_count"] == 1
    assert result.summary["under_review_count"] == 0
    triage_map = {row["sample_window_id"]: row["recommendation"] for row in result.triage_rows}
    assert triage_map["ca_train_window_001"] == "allow_training_under_current_role"
    assert triage_map["ca_train_window_004"] == "allow_training_under_current_role"
    assert triage_map["ca_train_window_006"] == "allow_training_under_current_role"
    assert triage_map["ca_train_window_002"] == "keep_hold_and_continue_policy_wording_lock"
    assert triage_map["ca_train_window_008"] == "allow_subwindow_learning_only"
