from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135bd_commercial_aerospace_bc_training_sample_package_direction_triage_v1 import (
    V135BDCommercialAerospaceBCTrainingSamplePackageDirectionTriageV1Analyzer,
)


def test_v135bd_training_sample_package_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135BDCommercialAerospaceBCTrainingSamplePackageDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["window_count"] == 10
    assert result.summary["primary_fit_count"] == 2
    assert result.summary["auxiliary_fit_count"] == 4
    assert result.summary["non_fit_count"] == 4
    triage_map = {row["sample_window_id"]: row["recommendation"] for row in result.triage_rows}
    assert triage_map["ca_train_window_002"] == "keep_locked_out_of_fit"
    assert triage_map["ca_train_window_008"] == "keep_for_reference_and_subwindow_learning_only"
    assert triage_map["ca_train_window_007"] == "keep_for_reference_and_subwindow_learning_only"
    assert triage_map["ca_train_window_005"] == "fit_directly_under_current_negative_role"
