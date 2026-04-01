from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114b_cpo_add_reduce_risk_acceptable_refinement_v1 import (
    V114BCPOAddReduceRiskAcceptableRefinementAnalyzer,
)


def test_v114b_cpo_add_reduce_risk_acceptable_refinement() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114BCPOAddReduceRiskAcceptableRefinementAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports/analysis/v113n_cpo_real_board_episode_population_v1.json"),
        v113v_payload=load_json_report(repo_root / "reports/analysis/v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114a_payload=load_json_report(repo_root / "reports/analysis/v114a_cpo_constrained_add_reduce_policy_search_pilot_v1.json"),
    )

    assert result.summary["tested_local_config_count"] >= 1
    assert result.summary["recommended_curve"] >= result.summary["baseline_curve"]
    assert len(result.frontier_rows) >= 1
