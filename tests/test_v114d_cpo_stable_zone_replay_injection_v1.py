from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114d_cpo_stable_zone_replay_injection_v1 import (
    V114DCPOStableZoneReplayInjectionAnalyzer,
)


def test_v114d_cpo_stable_zone_replay_injection() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114DCPOStableZoneReplayInjectionAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v113n_payload=load_json_report(repo_root / "reports/analysis/v113n_cpo_real_board_episode_population_v1.json"),
        v113v_payload=load_json_report(repo_root / "reports/analysis/v113v_cpo_full_board_execution_main_feed_replay_v1.json"),
        v114c_payload=load_json_report(repo_root / "reports/analysis/v114c_cpo_batched_local_policy_frontier_search_v1.json"),
    )

    assert result.summary["candidate_count"] == 3
    assert result.summary["recommended_curve"] >= result.summary["baseline_curve"]
    assert len(result.candidate_rows) == 3
