from pathlib import Path

from a_share_quant.strategy.v134cj_commercial_aerospace_local_rebound_residue_registry_v1 import (
    V134CJCommercialAerospaceLocalReboundResidueRegistryV1Analyzer,
)


def test_v134cj_commercial_aerospace_local_rebound_residue_registry_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CJCommercialAerospaceLocalReboundResidueRegistryV1Analyzer(repo_root).analyze()

    assert result.summary["residue_seed_count"] == 4
    assert result.summary["persistent_rebound_residue_count"] == 2
    assert result.summary["transient_rebound_residue_count"] == 2
    assert result.summary["top_residue_case"] == "20260120 300342"

