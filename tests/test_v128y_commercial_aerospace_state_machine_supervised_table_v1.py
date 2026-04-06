from pathlib import Path

from a_share_quant.strategy.v128y_commercial_aerospace_state_machine_supervised_table_v1 import (
    V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer,
)


def test_v128y_commercial_aerospace_state_machine_supervised_table_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128YCommercialAerospaceStateMachineSupervisedTableAnalyzer(repo_root).analyze()

    assert result.summary["row_count"] > 0
    assert int(result.summary["state_label_count"]) == 5
    assert int(result.summary["active_state_count"]) == 4
    assert int(result.summary["active_state_counts"]["full_pre"]) == 45
    assert int(result.summary["active_state_counts"]["full"]) == 36

