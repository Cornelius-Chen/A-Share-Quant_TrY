from pathlib import Path

from a_share_quant.strategy.v134cn_commercial_aerospace_reduce_handoff_package_v1 import (
    V134CNCommercialAerospaceReduceHandoffPackageV1Analyzer,
)


def test_v134cn_commercial_aerospace_reduce_handoff_package_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CNCommercialAerospaceReduceHandoffPackageV1Analyzer(repo_root).analyze()

    assert result.summary["reduce_mainline_frozen"] is True
    assert result.summary["local_residue_supervision_only"] is True
    assert result.summary["execution_blocker_count"] == 4
    assert result.summary["future_handoff_ready"] is True

