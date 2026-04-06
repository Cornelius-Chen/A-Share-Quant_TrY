from pathlib import Path

from a_share_quant.strategy.v125x_commercial_aerospace_eod_binary_action_pilot_v1 import (
    V125XCommercialAerospaceEODBinaryActionPilotAnalyzer,
)


def test_v125x_runs_binary_action_pilot() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125XCommercialAerospaceEODBinaryActionPilotAnalyzer(repo_root).analyze()
    assert result.summary["task_count"] == 2
