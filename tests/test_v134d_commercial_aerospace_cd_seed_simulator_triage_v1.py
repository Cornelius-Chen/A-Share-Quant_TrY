from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134d_commercial_aerospace_cd_seed_simulator_triage_v1 import (
    V134DCommercialAerospaceCDSeedSimulatorTriageAnalyzer,
)


def test_v134d_seed_simulator_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134DCommercialAerospaceCDSeedSimulatorTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == "retain_phase_2_seed_simulator_but_keep_replay_lane_blocked"
    assert result.triage_rows[0]["status"] == "retain_as_phase_2_seed_surface"
    assert result.triage_rows[3]["status"] == "still_blocked"
