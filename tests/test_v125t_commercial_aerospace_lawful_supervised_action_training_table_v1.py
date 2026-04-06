from pathlib import Path

from a_share_quant.strategy.v125t_commercial_aerospace_lawful_supervised_action_training_table_v1 import (
    V125TCommercialAerospaceLawfulSupervisedActionTrainingTableAnalyzer,
)


def test_v125t_builds_lawful_supervised_labels() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125TCommercialAerospaceLawfulSupervisedActionTrainingTableAnalyzer(repo_root).analyze()
    assert result.summary["row_count"] > 0
    assert result.summary["point_in_time_regime_proxy"] is True
