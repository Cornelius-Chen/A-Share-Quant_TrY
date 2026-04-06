from pathlib import Path

from a_share_quant.strategy.v129f_commercial_aerospace_def_walk_forward_direction_triage_v1 import (
    V129FCommercialAerospaceDEFWalkForwardDirectionTriageAnalyzer,
)


def test_v129f_commercial_aerospace_def_walk_forward_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129FCommercialAerospaceDEFWalkForwardDirectionTriageAnalyzer(repo_root).analyze()

    assert result.summary["supported_walk_forward_fold_count"] >= 1
    assert result.summary["authoritative_status"] == (
        "move_to_phase_specific_walk_forward_for_full_pre_only_and_keep_full_phase_contextual"
    )
