from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v117w_cpo_cooling_reacceleration_false_positive_control_discovery_v1 import (
    V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryAnalyzer,
)


def test_v117w_cooling_reacceleration_false_positive_control_discovery() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )

    assert result.summary["candidate_name"] == "cooling_reacceleration_overheat_control_candidate"
    assert result.summary["row_count"] >= 10
    assert "control_helpful" in result.summary

