from __future__ import annotations

from a_share_quant.strategy.v120d_cpo_dual_baseline_factor_registry_v1 import (
    CpoDualBaselineFactorRegistryAnalyzer,
)


def test_dual_baseline_registry_keeps_authoritative_baseline_single() -> None:
    analyzer = CpoDualBaselineFactorRegistryAnalyzer()
    result = analyzer.analyze(
        repaired_replay_payload={"summary": {"board_name": "CPO"}},
        cooling_triage_payload={"summary": {"cooling_reacceleration_branch_status": "candidate_only"}},
        sustained_triage_payload={"summary": {"branch_status": "candidate_only"}},
        elg_triage_payload={"summary": {"branch_status": "candidate_only"}},
        cooled_retention_payload={"summary": {"retained_variant_name": "cooled_q_0p25", "candidate_posture": "quality_side_cooled_candidate_only"}},
        breakout_soft_payload={"summary": {"breakout_damage_soft_component_status": "archived_soft_component"}},
    )
    authoritative_rows = [row for row in result.baseline_rows if row["baseline_name"] == "authoritative_baseline"]
    assert len(authoritative_rows) == 1
    assert authoritative_rows[0]["mainline_allowed"] is True
    assert result.summary["research_test_baseline_replay_facing_disabled"] is True


def test_dual_baseline_registry_contains_soft_component_bucket() -> None:
    analyzer = CpoDualBaselineFactorRegistryAnalyzer()
    result = analyzer.analyze(
        repaired_replay_payload={"summary": {"board_name": "CPO"}},
        cooling_triage_payload={"summary": {"cooling_reacceleration_branch_status": "candidate_only"}},
        sustained_triage_payload={"summary": {"branch_status": "candidate_only"}},
        elg_triage_payload={"summary": {"branch_status": "candidate_only"}},
        cooled_retention_payload={"summary": {"retained_variant_name": "cooled_q_0p25", "candidate_posture": "quality_side_cooled_candidate_only"}},
        breakout_soft_payload={"summary": {"breakout_damage_soft_component_status": "archived_soft_component"}},
    )
    soft_rows = [row for row in result.baseline_rows if row["component_class"] == "soft_expectancy_component"]
    assert len(soft_rows) == 1
    assert soft_rows[0]["component_name"] == "breakout_damage_soft_component"
