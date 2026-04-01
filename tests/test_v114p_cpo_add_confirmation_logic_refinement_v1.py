from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114p_cpo_add_confirmation_logic_refinement_v1 import (
    V114PCpoAddConfirmationLogicRefinementAnalyzer,
)


def test_v114p_cpo_add_confirmation_logic_refinement() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114PCpoAddConfirmationLogicRefinementAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114e_payload=load_json_report(repo_root / "reports" / "analysis" / "v114e_cpo_default_sizing_replay_promotion_v1.json"),
        v114m_payload=load_json_report(repo_root / "reports" / "analysis" / "v114m_cpo_posture_environment_split_review_v1.json"),
        v114n_payload=load_json_report(repo_root / "reports" / "analysis" / "v114n_cpo_vector_overlay_refinement_review_v1.json"),
        v114o_payload=load_json_report(repo_root / "reports" / "analysis" / "v114o_cpo_vector_overlay_execution_axis_review_v1.json"),
    )

    assert result.summary["candidate_count"] == 6
    assert any(row["candidate_name"] == "two_stage_confirmation" for row in result.candidate_rows)
    assert result.recommended_row["full_curve"] >= 2.3083
