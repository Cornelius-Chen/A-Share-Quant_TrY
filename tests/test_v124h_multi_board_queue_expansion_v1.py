from pathlib import Path

from a_share_quant.strategy.v124h_multi_board_queue_expansion_v1 import (
    V124HMultiBoardQueueExpansionAnalyzer,
)


def test_v124h_queue_expansion_selects_commercial_aerospace_first() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V124HMultiBoardQueueExpansionAnalyzer(repo_root).analyze()

    assert result.summary["next_primary_board"] == "商业航天"
    assert result.summary["next_primary_sector_id"] == "BK0963"
    assert result.queue_rows[1]["board_name"] == "商业航天"
    assert result.queue_rows[1]["queue_status"] == "queued"
    assert result.board_candidate_rows[0]["recommended_core_symbols"][0] == "002085"
