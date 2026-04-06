from pathlib import Path

from a_share_quant.strategy.v125e_commercial_aerospace_boundary_triage_v1 import (
    V125ECommercialAerospaceBoundaryTriageAnalyzer,
)


def test_v125e_keeps_replay_blocked() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125ECommercialAerospaceBoundaryTriageAnalyzer(repo_root).analyze()
    assert result.summary["allow_replay_now"] is False
