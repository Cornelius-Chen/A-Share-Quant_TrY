from pathlib import Path

from a_share_quant.strategy.v134fs_commercial_aerospace_fr_wave_state_direction_triage_v1 import (
    V134FSCommercialAerospaceFRWaveStateDirectionTriageV1Analyzer,
)


def test_v134fs_commercial_aerospace_fr_wave_state_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FSCommercialAerospaceFRWaveStateDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_post_wave_echo_guard_and_shift_next_to_active_wave_selection_supervision"
    )
