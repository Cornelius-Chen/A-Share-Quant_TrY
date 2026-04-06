from pathlib import Path

from a_share_quant.strategy.v126b_commercial_aerospace_regime_conditioned_binary_pilot_v1 import (
    V126BCommercialAerospaceRegimeConditionedBinaryPilotAnalyzer,
)


def test_v126b_runs_regime_conditioned_binary_pilot() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V126BCommercialAerospaceRegimeConditionedBinaryPilotAnalyzer(repo_root).analyze()
    assert result.summary["train_row_count"] > 0
