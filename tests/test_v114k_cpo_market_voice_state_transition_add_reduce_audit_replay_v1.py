from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114k_cpo_market_voice_state_transition_add_reduce_audit_replay_v1 import (
    V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayAnalyzer,
)


def test_v114k_cpo_market_voice_state_transition_add_reduce_audit_replay() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114KCpoMarketVoiceStateTransitionAddReduceAuditReplayAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports" / "analysis" / "v113n_cpo_real_board_episode_population_v1.json"),
        v113v_payload=load_json_report(repo_root / "reports" / "analysis" / "v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114e_payload=load_json_report(repo_root / "reports" / "analysis" / "v114e_cpo_default_sizing_replay_promotion_v1.json"),
        v114h_payload=load_json_report(repo_root / "reports" / "analysis" / "v114h_cpo_promoted_sizing_behavior_audit_v1.json"),
        v114j_payload=load_json_report(repo_root / "reports" / "analysis" / "v114j_cpo_market_voice_state_transition_vector_prototype_v1.json"),
    )

    assert result.summary["candidate_curve"] >= result.summary["promoted_curve"]
    assert result.candidate_policy_summary["candidate_add_band_days"] > 0
    assert result.candidate_policy_summary["candidate_remaining_under_exposed_count"] <= result.candidate_policy_summary["promoted_remaining_under_exposed_count"]
