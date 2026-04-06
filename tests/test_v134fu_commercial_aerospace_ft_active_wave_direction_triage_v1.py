from pathlib import Path

from a_share_quant.strategy.v134fu_commercial_aerospace_ft_active_wave_direction_triage_v1 import (
    V134FUCommercialAerospaceFTActiveWaveDirectionTriageV1Analyzer,
)


def test_v134fu_commercial_aerospace_ft_active_wave_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FUCommercialAerospaceFTActiveWaveDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_active_wave_selection_states_as_local_supervision_and_keep_add_execution_blocked"
    )
