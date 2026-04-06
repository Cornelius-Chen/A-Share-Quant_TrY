from pathlib import Path

from a_share_quant.strategy.v124a_cpo_yza_heat_conditioned_riskoff_triage_v1 import (
    V124ACpoYzaHeatConditionedRiskoffTriageAnalyzer,
)


def test_v124a_heat_conditioned_riskoff_triage_is_shadow_only() -> None:
    result = V124ACpoYzaHeatConditionedRiskoffTriageAnalyzer().analyze()

    assert result.summary["authoritative_status"] == "shadow_only_not_promotable"
    assert result.summary["majority_vote"]["shadow_only_not_promotable"] == 3
    assert result.summary["heat_replay_facing_allowed"] is True
    assert result.summary["heat_conditioned_riskoff_replay_facing_allowed"] is False
