from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114c_cpo_batched_local_policy_frontier_search_v1 import (
    V114CCPOBatchedLocalPolicyFrontierSearchAnalyzer,
)


def test_v114c_cpo_batched_local_policy_frontier_search_plan_shape() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114CCPOBatchedLocalPolicyFrontierSearchAnalyzer(repo_root=repo_root)
    v114a_payload = load_json_report(repo_root / "reports/analysis/v114a_cpo_constrained_add_reduce_policy_search_pilot_v1.json")
    best_config = dict(v114a_payload.get("best_config_row", {}).get("config", {}))

    plan = analyzer._build_batch_plan(best_config=best_config)

    assert len(plan) >= 10
    assert len({(row["config"]["strong_board_uplift"], row["config"]["derisk_keep_fraction"], row["config"]["under_exposure_floor"]) for row in plan}) == len(plan)
