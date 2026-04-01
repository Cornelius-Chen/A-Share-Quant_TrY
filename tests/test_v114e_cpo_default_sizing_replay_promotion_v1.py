from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114e_cpo_default_sizing_replay_promotion_v1 import (
    V114ECPODefaultSizingReplayPromotionAnalyzer,
)


def test_v114e_cpo_default_sizing_replay_promotion() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114ECPODefaultSizingReplayPromotionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114d_payload=load_json_report(repo_root / "reports" / "analysis" / "v114d_cpo_stable_zone_replay_injection_v1.json"),
    )

    assert result.summary["promoted_default_candidate_name"] == "expectancy_max_injection"
    assert result.baseline_comparison_row["promoted_curve"] > result.baseline_comparison_row["baseline_curve"]
    assert result.promotion_checks["drawdown_uplift_is_positive_but_controlled"] is True
