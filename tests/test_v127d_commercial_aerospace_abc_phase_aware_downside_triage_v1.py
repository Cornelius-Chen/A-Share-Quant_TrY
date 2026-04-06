from pathlib import Path

from a_share_quant.strategy.v127d_commercial_aerospace_abc_phase_aware_downside_triage_v1 import (
    V127DCommercialAerospaceABCPhaseAwareDownsideTriageAnalyzer,
)


def test_v127d_phase_aware_downside_triage_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V127DCommercialAerospaceABCPhaseAwareDownsideTriageAnalyzer(repo_root).analyze()
    assert result.summary["new_aggressive_shadow_variant"] == "broad_half_reference"
