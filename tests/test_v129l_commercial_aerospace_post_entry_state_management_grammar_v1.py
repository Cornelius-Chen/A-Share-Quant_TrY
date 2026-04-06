from pathlib import Path

from a_share_quant.strategy.v129l_commercial_aerospace_post_entry_state_management_grammar_v1 import (
    V129LCommercialAerospacePostEntryStateManagementGrammarAnalyzer,
)


def test_v129l_commercial_aerospace_post_entry_state_management_grammar_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129LCommercialAerospacePostEntryStateManagementGrammarAnalyzer(repo_root).analyze()

    assert result.summary["state_management_focus"] == "post_entry_upgrade_derisk_tail_repair_governance"
    assert len(result.grammar_rows) == 5
