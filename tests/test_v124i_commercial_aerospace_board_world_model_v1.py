from pathlib import Path

from a_share_quant.strategy.v124i_commercial_aerospace_board_world_model_v1 import (
    V124ICommercialAerospaceBoardWorldModelAnalyzer,
)


def test_v124i_commercial_aerospace_world_model_starts_with_expected_roles() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124ICommercialAerospaceBoardWorldModelAnalyzer(repo_root).analyze()

    assert result.summary["board_name"] == "商业航天"
    assert result.summary["sector_id"] == "BK0963"
    assert result.board_label_summary["primary_liquid_leader"] == "002085"
    assert result.board_label_summary["stable_core_support"] == "000738"
