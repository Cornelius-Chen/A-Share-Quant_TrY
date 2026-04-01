from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114m_cpo_posture_environment_split_review_v1 import (
    V114MCpoPostureEnvironmentSplitReviewAnalyzer,
)


def test_v114m_cpo_posture_environment_split_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114MCpoPostureEnvironmentSplitReviewAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114d_payload=load_json_report(repo_root / "reports" / "analysis" / "v114d_cpo_stable_zone_replay_injection_v1.json"),
        v114e_payload=load_json_report(repo_root / "reports" / "analysis" / "v114e_cpo_default_sizing_replay_promotion_v1.json"),
        v114j_payload=load_json_report(repo_root / "reports" / "analysis" / "v114j_cpo_market_voice_state_transition_vector_prototype_v1.json"),
    )

    assert result.summary["posture_count"] >= 4
    assert any(row["segment_name"] == "high_readiness_strong" for row in result.segment_leader_rows)
    assert any(row["leading_posture_name"] == "vector_overlay_experimental" for row in result.segment_leader_rows)
