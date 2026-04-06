from pathlib import Path

from a_share_quant.strategy.v129s_bk0480_aerospace_aviation_role_grammar_v1 import (
    V129SBK0480AerospaceAviationRoleGrammarAnalyzer,
)


def test_v129s_bk0480_aerospace_aviation_role_grammar_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129SBK0480AerospaceAviationRoleGrammarAnalyzer(repo_root).analyze()

    assert result.summary["sector_id"] == "BK0480"
    assert result.summary["internal_owner_count"] == 2
    assert result.summary["confirmation_count"] == 0
    assert result.relative_structure_labels[0]["members"] == ["000738", "600118"]
