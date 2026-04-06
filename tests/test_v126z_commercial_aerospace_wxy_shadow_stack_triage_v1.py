from pathlib import Path

from a_share_quant.strategy.v126z_commercial_aerospace_wxy_shadow_stack_triage_v1 import (
    V126ZCommercialAerospaceWXYShadowStackTriageAnalyzer,
)


def test_v126z_shadow_stack_triage_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126ZCommercialAerospaceWXYShadowStackTriageAnalyzer(repo_root).analyze()
    assert result.summary["economic_reference_variant"] == "v126o_economic_reference"
