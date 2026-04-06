from pathlib import Path

from a_share_quant.strategy.v129k_commercial_aerospace_governance_stack_packaging_v1 import (
    V129KCommercialAerospaceGovernanceStackPackagingAnalyzer,
)


def test_v129k_commercial_aerospace_governance_stack_packaging_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129KCommercialAerospaceGovernanceStackPackagingAnalyzer(repo_root).analyze()

    assert result.summary["governance_layer_count"] == 7
    assert len(result.governance_rows) == 7
