from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134f_commercial_aerospace_ef_seed_simulator_direction_triage_v1 import (
    V134FCommercialAerospaceEFSeedSimulatorDirectionTriageAnalyzer,
)


def test_v134f_seed_simulator_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134FCommercialAerospaceEFSeedSimulatorDirectionTriageAnalyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_seed_simulator_and_attribution_inside_phase_2_but_keep_broader_expansion_and_replay_blocked"
    )
    assert result.triage_rows[1]["status"] == "accepted_after_correction"
    assert result.triage_rows[3]["status"] == "still_blocked"
    assert result.triage_rows[4]["status"] == "still_blocked"
