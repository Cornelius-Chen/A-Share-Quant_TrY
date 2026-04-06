from pathlib import Path

from a_share_quant.strategy.v134ej_commercial_aerospace_intraday_add_supervision_registry_v1 import (
    V134EJCommercialAerospaceIntradayAddSupervisionRegistryV1Analyzer,
)


def test_v134ej_commercial_aerospace_intraday_add_supervision_registry_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134EJCommercialAerospaceIntradayAddSupervisionRegistryV1Analyzer(repo_root).analyze()

    assert result.summary["registry_row_count"] == 55
    assert result.summary["seed_family_count"] == 3
    assert result.summary["failed_add_seed_count"] == 2
    assert result.summary["blocked_add_seed_count"] == 4
