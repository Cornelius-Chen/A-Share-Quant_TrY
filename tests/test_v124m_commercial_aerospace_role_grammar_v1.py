from pathlib import Path

from a_share_quant.strategy.v124m_commercial_aerospace_role_grammar_v1 import (
    V124MCommercialAerospaceRoleGrammarAnalyzer,
)


def test_v124m_role_grammar_separates_internal_owners_from_cross_board_allies() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124MCommercialAerospaceRoleGrammarAnalyzer(repo_root).analyze()

    roles = {row["symbol"]: row for row in result.role_rows}
    assert roles["002085"]["role_label"] == "direct_liquid_leader"
    assert roles["002565"]["role_label"] == "cross_board_propulsion_ally"
    assert roles["001208"]["role_label"] == "shovel_supplier_support"
    assert result.summary["next_phase"] == "control_extraction"
