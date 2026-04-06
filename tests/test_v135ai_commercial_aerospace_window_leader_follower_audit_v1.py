from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ai_commercial_aerospace_window_leader_follower_audit_v1 import (
    V135AICommercialAerospaceWindowLeaderFollowerAuditV1Analyzer,
)


def test_v135ai_leader_follower_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AICommercialAerospaceWindowLeaderFollowerAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 7
    assert result.summary["covered_window_count"] == 1
    assert result.summary["december_leader_count"] == 1
    assert result.summary["december_follower_count"] == 3
    assert result.summary["february_leader_deterioration_count"] == 1
    assert result.summary["february_follower_failure_count"] == 2
    assert result.summary["full_window_hold_count"] == 1
