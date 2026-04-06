from pathlib import Path

from a_share_quant.strategy.v125w_commercial_aerospace_eod_supervised_training_pilot_v1 import (
    V125WCommercialAerospaceEODSupervisedTrainingPilotAnalyzer,
)


def test_v125w_runs_eod_supervised_training_pilot() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125WCommercialAerospaceEODSupervisedTrainingPilotAnalyzer(repo_root).analyze()
    assert result.summary["train_row_count"] > 0
    assert result.summary["test_row_count"] > 0
