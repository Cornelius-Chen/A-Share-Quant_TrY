from pathlib import Path

from a_share_quant.strategy.v125r_commercial_aerospace_supervised_leakage_triage_v1 import (
    V125RCommercialAerospaceSupervisedLeakageTriageAnalyzer,
)


def test_v125r_blocks_full_sample_regime_semantic_for_lawful_training() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125RCommercialAerospaceSupervisedLeakageTriageAnalyzer(repo_root).analyze()
    assert result.summary["hard_lookahead_detected"] is False
    assert result.summary["semantic_point_in_time_risk_detected"] is True
