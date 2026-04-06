from pathlib import Path

from a_share_quant.strategy.v129t_bk0480_aerospace_aviation_stu_role_triage_v1 import (
    V129TBK0480AerospaceAviationSTURoleTriageAnalyzer,
)


def test_v129t_bk0480_aerospace_aviation_stu_role_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129TBK0480AerospaceAviationSTURoleTriageAnalyzer(repo_root).analyze()

    assert result.summary["authoritative_status"] == (
        "freeze_bk0480_dual_core_role_grammar_and_move_to_control_seed_extraction"
    )
    assert any(row["direction"] == "borrowed_confirmation_or_mirror_layers" for row in result.direction_rows)
