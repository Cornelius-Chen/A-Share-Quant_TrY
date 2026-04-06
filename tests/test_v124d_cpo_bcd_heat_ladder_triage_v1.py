from a_share_quant.strategy.v124d_cpo_bcd_heat_ladder_triage_v1 import (
    V124DCpoBcdHeatLadderTriageAnalyzer,
)


def test_v124d_heat_ladder_triage_keeps_balanced_reference_frozen() -> None:
    result = V124DCpoBcdHeatLadderTriageAnalyzer().analyze()

    assert result.summary["authoritative_status"] == "keep_balanced_ladder_frozen"
    assert result.summary["majority_vote"]["keep_balanced_ladder_frozen"] == 3
    assert result.summary["balanced_heat_reference_replay_facing_allowed"] is True
    assert result.summary["alternative_ladder_replay_facing_allowed"] is False
