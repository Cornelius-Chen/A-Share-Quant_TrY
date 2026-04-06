from pathlib import Path

from a_share_quant.strategy.v129o_commercial_aerospace_bk0480_portability_boundary_memo_v1 import (
    V129OCommercialAerospaceBK0480PortabilityBoundaryMemoAnalyzer,
)


def test_v129o_commercial_aerospace_bk0480_portability_boundary_memo_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129OCommercialAerospaceBK0480PortabilityBoundaryMemoAnalyzer(repo_root).analyze()

    assert result.summary["selected_transfer_target"] == "BK0480"
    assert result.summary["portable_layer_count"] == 5
    assert any(row["layer"] == "phase_state_machine" for row in result.governance_carry_rows)
