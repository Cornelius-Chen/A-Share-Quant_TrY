from pathlib import Path

from a_share_quant.strategy.v131y_commercial_aerospace_intraday_supervision_registry_v1 import (
    V131YCommercialAerospaceIntradaySupervisionRegistryAnalyzer,
)


def test_v131y_intraday_supervision_registry() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131YCommercialAerospaceIntradaySupervisionRegistryAnalyzer(repo_root).analyze()

    assert result.summary["registry_row_count"] == 6
    assert result.summary["severe_override_positive_count"] == 2
    assert result.summary["reversal_watch_count"] == 2
    assert result.summary["mild_override_watch_count"] == 2

