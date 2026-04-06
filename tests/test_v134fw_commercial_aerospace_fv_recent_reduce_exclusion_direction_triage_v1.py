from pathlib import Path

from a_share_quant.strategy.v134fw_commercial_aerospace_fv_recent_reduce_exclusion_direction_triage_v1 import (
    V134FWCommercialAerospaceFVRecentReduceExclusionDirectionTriageV1Analyzer,
)


def test_v134fw_commercial_aerospace_fv_recent_reduce_exclusion_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FWCommercialAerospaceFVRecentReduceExclusionDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_recent_reduce_residue_as_local_active_wave_exclusion_clue_and_keep_add_execution_blocked"
    )
