from pathlib import Path

from a_share_quant.strategy.v134cs_commercial_aerospace_reduce_reopen_playbook_v1 import (
    V134CSCommercialAerospaceReduceReopenPlaybookV1Analyzer,
)


def test_v134cs_commercial_aerospace_reduce_reopen_playbook_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134CSCommercialAerospaceReduceReopenPlaybookV1Analyzer(repo_root).analyze()

    assert result.summary["residue_seed_count"] == 4
    assert result.summary["execution_blocker_count"] == 4
    assert any(row["reopen_scope"] == "broad_reduce_semantics" and row["allowed_action"] == "keep_frozen" for row in result.playbook_rows)
