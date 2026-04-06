from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135am_commercial_aerospace_window_policy_anchor_lock_audit_v1 import (
    V135AMCommercialAerospaceWindowPolicyAnchorLockAuditV1Analyzer,
)


def test_v135am_policy_anchor_lock_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AMCommercialAerospaceWindowPolicyAnchorLockAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 4
    assert result.summary["covered_window_count"] == 1
    assert result.summary["direction_anchor_count"] == 2
    assert result.summary["reinforcement_anchor_count"] == 2
    assert result.summary["exact_january_ignition_text_locked_count"] == 0
    assert result.summary["gate_hold_count"] == 1

