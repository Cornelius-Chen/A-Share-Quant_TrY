from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134b_commercial_aerospace_ab_simulator_direction_triage_v1 import (
    V134BCommercialAerospaceABSimulatorDirectionTriageAnalyzer,
)


def test_v134b_simulator_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134BCommercialAerospaceABSimulatorDirectionTriageAnalyzer(repo_root).analyze()

    assert result.summary["reviewer_count"] == 3
    assert result.summary["consensus_count"] == 4
    assert (
        result.summary["authoritative_status"]
        == "approve_phase_2_simulator_implementation_but_keep_phase_3_replay_lane_blocked"
    )
    assert result.consensus_rows[0]["status"] == "approved_for_implementation"
    assert result.consensus_rows[1]["status"] == "mandatory"
    assert result.consensus_rows[3]["status"] == "still_blocked"
