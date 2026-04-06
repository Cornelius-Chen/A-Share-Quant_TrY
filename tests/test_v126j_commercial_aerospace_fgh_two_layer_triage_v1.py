from pathlib import Path

from a_share_quant.strategy.v126j_commercial_aerospace_fgh_two_layer_triage_v1 import (
    V126JCommercialAerospaceFGHTwoLayerTriageAnalyzer,
)


def test_v126j_two_layer_triage_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V126JCommercialAerospaceFGHTwoLayerTriageAnalyzer(repo_root).analyze()
    assert result.summary["baseline_final_equity"] > 0
    assert result.summary["best_variant_final_equity"] > 0
