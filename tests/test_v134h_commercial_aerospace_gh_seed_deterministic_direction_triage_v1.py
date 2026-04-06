from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134h_commercial_aerospace_gh_seed_deterministic_direction_triage_v1 import (
    V134HCommercialAerospaceGHSeedDeterministicDirectionTriageAnalyzer,
)


def test_v134h_seed_deterministic_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134HCommercialAerospaceGHSeedDeterministicDirectionTriageAnalyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "retain_deterministic_seed_simulation_inside_phase_2_but_keep_expansion_and_replay_blocked"
    )
    assert result.triage_rows[0]["status"] == "accepted"
    assert result.triage_rows[3]["status"] == "still_blocked"
    assert result.triage_rows[4]["status"] == "still_blocked"
