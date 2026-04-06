from a_share_quant.strategy.v124p_commercial_aerospace_lmn_universe_triage_v1 import (
    V124PCommercialAerospaceLmnUniverseTriageAnalyzer,
)


def test_v124p_universe_triage_is_required_before_control() -> None:
    result = V124PCommercialAerospaceLmnUniverseTriageAnalyzer().analyze()

    assert result.summary["authoritative_status"] == "universe_triage_first"
    assert result.summary["majority_vote"]["universe_triage_first"] == 3
    assert result.summary["allow_control_extraction_now"] is False
