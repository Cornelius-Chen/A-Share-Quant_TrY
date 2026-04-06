from pathlib import Path

from a_share_quant.strategy.v126y_commercial_aerospace_shadow_stack_compare_v1 import (
    V126YCommercialAerospaceShadowStackCompareAnalyzer,
)


def test_v126y_shadow_stack_compare_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126YCommercialAerospaceShadowStackCompareAnalyzer(repo_root).analyze()
    assert len(result.stack_rows) == 4
