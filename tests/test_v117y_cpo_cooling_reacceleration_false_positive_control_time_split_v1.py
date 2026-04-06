from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v117w_cpo_cooling_reacceleration_false_positive_control_discovery_v1 import (
    V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryAnalyzer,
)
from a_share_quant.strategy.v117y_cpo_cooling_reacceleration_false_positive_control_time_split_v1 import (
    V117YCpoCoolingReaccelerationFalsePositiveControlTimeSplitAnalyzer,
)


def test_v117y_cooling_reacceleration_false_positive_control_time_split() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    upstream = V117WCpoCoolingReaccelerationFalsePositiveControlDiscoveryAnalyzer(repo_root=repo_root).analyze(
        rows_path=repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_feature_base_table_v1.csv",
    )
    analyzer = V117YCpoCoolingReaccelerationFalsePositiveControlTimeSplitAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(v117w_payload=upstream.as_dict())

    assert result.summary["split_count"] == 3
    assert 0.0 <= result.summary["mean_test_balanced_accuracy"] <= 1.0
