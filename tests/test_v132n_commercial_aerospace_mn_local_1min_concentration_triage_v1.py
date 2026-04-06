from pathlib import Path

from a_share_quant.strategy.v132n_commercial_aerospace_mn_local_1min_concentration_triage_v1 import (
    V132NCommercialAerospaceMNLocal1MinConcentrationTriageAnalyzer,
)


def test_v132n_local_1min_concentration_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132NCommercialAerospaceMNLocal1MinConcentrationTriageAnalyzer(repo_root).analyze()

    assert result.summary["expanded_hit_count"] == 24
    assert result.summary["main_window_hit_share"] >= 0.0
