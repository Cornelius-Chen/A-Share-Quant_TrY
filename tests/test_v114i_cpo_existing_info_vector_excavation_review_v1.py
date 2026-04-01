from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114i_cpo_existing_info_vector_excavation_review_v1 import (
    V114ICPOExistingInfoVectorExcavationReviewAnalyzer,
)


def test_v114i_cpo_existing_info_vector_excavation_review() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114ICPOExistingInfoVectorExcavationReviewAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114h_payload=load_json_report(repo_root / "reports" / "analysis" / "v114h_cpo_promoted_sizing_behavior_audit_v1.json"),
    )

    assert result.summary["candidate_vector_count"] == 5
    assert result.summary["existing_info_has_actionable_vector_headroom"] is True
    assert result.intraday_boundary["intraday_required_now"] is False
