from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v117s_cpo_cooling_reacceleration_discovery_v1 import (
    V117SCpoCoolingReaccelerationDiscoveryAnalyzer,
)


def test_v117s_cooling_reacceleration_discovery() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V117SCpoCoolingReaccelerationDiscoveryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )

    assert result.summary["candidate_discriminator_name"] == "cooling_reacceleration_score_candidate"
    assert result.summary["add_row_count"] >= 10
    assert result.summary["positive_add_row_count"] >= 4

