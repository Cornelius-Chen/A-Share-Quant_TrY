from pathlib import Path

from a_share_quant.strategy.v127b_commercial_aerospace_xyz_phase_aware_derisk_triage_v1 import (
    V127BCommercialAerospaceXYZPhaseAwareDeriskTriageAnalyzer,
)


def test_v127b_phase_aware_derisk_triage_runs():
    repo_root = Path(__file__).resolve().parents[1]
    result = V127BCommercialAerospaceXYZPhaseAwareDeriskTriageAnalyzer(repo_root).analyze()
    assert result.summary["replaces_old_aggressive_shadow"] is True
