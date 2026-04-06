from pathlib import Path

from a_share_quant.strategy.v125p_commercial_aerospace_supervised_action_training_table_v1 import (
    V125PCommercialAerospaceSupervisedActionTrainingTableAnalyzer,
)


def test_v125p_builds_supervised_labels() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125PCommercialAerospaceSupervisedActionTrainingTableAnalyzer(repo_root).analyze()
    assert result.summary["row_count"] > 0
    assert "full_eligibility_target" in result.summary["label_counts"]
