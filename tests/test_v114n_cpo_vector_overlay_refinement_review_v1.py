from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114n_cpo_vector_overlay_refinement_review_v1 import (
    V114NCpoVectorOverlayRefinementReviewAnalyzer,
)


def test_v114n_cpo_vector_overlay_refinement_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114NCpoVectorOverlayRefinementReviewAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114e_payload=load_json_report(repo_root / "reports" / "analysis" / "v114e_cpo_default_sizing_replay_promotion_v1.json"),
        v114j_payload=load_json_report(repo_root / "reports" / "analysis" / "v114j_cpo_market_voice_state_transition_vector_prototype_v1.json"),
        v114m_payload=load_json_report(repo_root / "reports" / "analysis" / "v114m_cpo_posture_environment_split_review_v1.json"),
    )

    assert result.summary["candidate_count"] == 12
    assert result.recommended_row["beats_default_all_strong"] is True
    assert result.recommended_row["beats_default_high_readiness"] is True
    assert any(float(row["drawdown_reduction_vs_vector"]) > 0.0 for row in result.candidate_rows)
