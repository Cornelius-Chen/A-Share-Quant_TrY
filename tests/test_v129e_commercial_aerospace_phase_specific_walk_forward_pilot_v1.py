from pathlib import Path

from a_share_quant.strategy.v129e_commercial_aerospace_phase_specific_walk_forward_pilot_v1 import (
    V129ECommercialAerospacePhaseSpecificWalkForwardPilotAnalyzer,
)


def test_v129e_commercial_aerospace_phase_specific_walk_forward_pilot_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129ECommercialAerospacePhaseSpecificWalkForwardPilotAnalyzer(repo_root).analyze()

    assert result.summary["fold_count"] == 2
    assert len(result.fold_rows) == 2
    assert result.summary["authoritative_status"] == "full_pre_partial_learnability_but_full_still_too_thin"
