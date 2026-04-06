from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135aj_commercial_aerospace_ai_window_leader_follower_direction_triage_v1 import (
    V135AJCommercialAerospaceAIWindowLeaderFollowerDirectionTriageV1Analyzer,
)


def test_v135aj_leader_follower_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AJCommercialAerospaceAIWindowLeaderFollowerDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["window_count"] == 1
    assert result.summary["full_window_hold_count"] == 1
    assert result.triage_rows[0]["sample_window_id"] == "ca_train_window_008"
    assert "keep_subwindow_learning_only" in result.triage_rows[0]["recommendation"]
