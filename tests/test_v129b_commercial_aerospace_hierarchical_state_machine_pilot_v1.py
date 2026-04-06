from pathlib import Path

from a_share_quant.strategy.v129b_commercial_aerospace_hierarchical_state_machine_pilot_v1 import (
    V129BCommercialAerospaceHierarchicalStateMachinePilotAnalyzer,
)


def test_v129b_commercial_aerospace_hierarchical_state_machine_pilot_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129BCommercialAerospaceHierarchicalStateMachinePilotAnalyzer(repo_root).analyze()

    assert result.summary["train_row_count"] > 0
    assert result.summary["test_row_count"] > 0
    assert int(result.summary["label_count"]) == 5
