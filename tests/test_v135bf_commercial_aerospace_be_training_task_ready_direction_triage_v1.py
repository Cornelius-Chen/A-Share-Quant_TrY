from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135bf_commercial_aerospace_be_training_task_ready_direction_triage_v1 import (
    V135BFCommercialAerospaceBETrainingTaskReadyDirectionTriageV1Analyzer,
)


def test_v135bf_training_task_ready_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135BFCommercialAerospaceBETrainingTaskReadyDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["task_count"] == 6
    assert result.summary["tasks_with_primary_fit"] == 4
    assert result.summary["tasks_with_auxiliary_fit"] == 5
    assert result.summary["tasks_with_reference_only"] == 5
    assert result.summary["tasks_with_locked_holdout"] == 6
    triage_map = {row["task_id"]: row["recommendation"] for row in result.triage_rows}
    assert triage_map["ca_task_001"] == "use_reference_and_holdout_only_until_primary_positive_archetype_unlocks"
    assert triage_map["ca_task_006"] == "fit_bridge_auxiliary_cautiously_and_keep_positive_examples_as_reference_only"
    assert triage_map["ca_task_002"] == "fit_direct_negatives_with_auxiliary_context_under_current_strict_boundary"
