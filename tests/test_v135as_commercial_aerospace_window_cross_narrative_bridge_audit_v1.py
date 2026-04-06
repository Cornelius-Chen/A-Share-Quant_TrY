from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135as_commercial_aerospace_window_cross_narrative_bridge_audit_v1 import (
    V135ASCommercialAerospaceWindowCrossNarrativeBridgeAuditV1Analyzer,
)


def test_v135as_cross_narrative_bridge_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135ASCommercialAerospaceWindowCrossNarrativeBridgeAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 5
    assert result.summary["covered_window_count"] == 1
    assert result.summary["not_tradable_count"] == 1
    assert result.summary["watch_only_count"] == 4
    assert result.summary["bridge_sample_ready_count"] == 1

