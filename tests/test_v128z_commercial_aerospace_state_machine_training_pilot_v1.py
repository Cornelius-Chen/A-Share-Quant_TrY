from pathlib import Path

from a_share_quant.strategy.v128z_commercial_aerospace_state_machine_training_pilot_v1 import (
    V128ZCommercialAerospaceStateMachineTrainingPilotAnalyzer,
)


def test_v128z_commercial_aerospace_state_machine_training_pilot_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128ZCommercialAerospaceStateMachineTrainingPilotAnalyzer(repo_root).analyze()

    assert result.summary["train_row_count"] > 0
    assert result.summary["test_row_count"] > 0
    assert int(result.summary["label_count"]) == 5
