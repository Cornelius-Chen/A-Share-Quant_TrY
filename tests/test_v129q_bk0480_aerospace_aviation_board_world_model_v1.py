from pathlib import Path

from a_share_quant.strategy.v129q_bk0480_aerospace_aviation_board_world_model_v1 import (
    V129QBK0480AerospaceAviationBoardWorldModelAnalyzer,
)


def test_v129q_bk0480_aerospace_aviation_board_world_model_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129QBK0480AerospaceAviationBoardWorldModelAnalyzer(repo_root).analyze()

    assert result.summary["sector_id"] == "BK0480"
    assert result.summary["role_row_count"] == 2
    assert result.role_rows[0]["symbol"] == "000738"
