from pathlib import Path

from a_share_quant.strategy.v129n_commercial_aerospace_transfer_target_selection_v1 import (
    V129NCommercialAerospaceTransferTargetSelectionAnalyzer,
)


def test_v129n_commercial_aerospace_transfer_target_selection_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V129NCommercialAerospaceTransferTargetSelectionAnalyzer(repo_root).analyze()

    assert result.summary["recommended_primary_transfer_target"] == "BK0480"
    assert result.candidate_rows[0]["sector_id"] == "BK0480"
    assert any(row["blocked_direction"] == "chronology_clone" for row in result.blocked_rows)
