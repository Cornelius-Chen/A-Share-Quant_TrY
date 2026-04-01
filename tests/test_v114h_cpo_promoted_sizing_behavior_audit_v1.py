from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114h_cpo_promoted_sizing_behavior_audit_v1 import (
    V114HCPOPromotedSizingBehaviorAuditAnalyzer,
)


def test_v114h_cpo_promoted_sizing_behavior_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114HCPOPromotedSizingBehaviorAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114e_payload=load_json_report(repo_root / "reports" / "analysis" / "v114e_cpo_default_sizing_replay_promotion_v1.json"),
    )

    assert result.summary["promoted_curve"] > result.summary["baseline_curve"]
    assert result.behavior_summary["strong_board_day_count"] > 0
    assert len(result.promoted_action_rows) >= 10
