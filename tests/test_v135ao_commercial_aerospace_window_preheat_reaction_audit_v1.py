from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ao_commercial_aerospace_window_preheat_reaction_audit_v1 import (
    V135AOCommercialAerospaceWindowPreheatReactionAuditV1Analyzer,
)


def test_v135ao_preheat_reaction_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AOCommercialAerospaceWindowPreheatReactionAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 5
    assert result.summary["covered_window_count"] == 1
    assert result.summary["formal_or_industrial_confirmation_count"] == 3
    assert result.summary["emotion_confirmation_count"] == 2
    assert result.summary["gate_hold_count"] == 1

