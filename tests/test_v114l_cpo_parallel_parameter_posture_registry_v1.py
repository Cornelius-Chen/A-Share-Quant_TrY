from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114a_cpo_constrained_add_reduce_policy_search_pilot_v1 import (
    load_json_report,
)
from a_share_quant.strategy.v114l_cpo_parallel_parameter_posture_registry_v1 import (
    V114LCpoParallelParameterPostureRegistryAnalyzer,
)


def test_v114l_cpo_parallel_parameter_posture_registry() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114LCpoParallelParameterPostureRegistryAnalyzer(repo_root=repo_root)
    result = analyzer.analyze(
        v114d_payload=load_json_report(repo_root / "reports" / "analysis" / "v114d_cpo_stable_zone_replay_injection_v1.json"),
        v114e_payload=load_json_report(repo_root / "reports" / "analysis" / "v114e_cpo_default_sizing_replay_promotion_v1.json"),
        v114k_payload=load_json_report(repo_root / "reports" / "analysis" / "v114k_cpo_market_voice_state_transition_add_reduce_audit_replay_v1.json"),
    )

    assert result.summary["default_posture_name"] == "default_expectancy_mainline"
    assert result.summary["retained_posture_count"] >= 4
    assert any(row["status"] == "candidate_only" for row in result.posture_rows)
    vector_row = next(row for row in result.posture_rows if row["posture_name"] == "vector_overlay_experimental")
    assert float(vector_row["config"]["candidate_add_threshold"]) > 0.0
