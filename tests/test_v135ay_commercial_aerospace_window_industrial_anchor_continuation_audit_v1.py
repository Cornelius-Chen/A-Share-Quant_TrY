from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ay_commercial_aerospace_window_industrial_anchor_continuation_audit_v1 import (
    V135AYCommercialAerospaceWindowIndustrialAnchorContinuationAuditV1Analyzer,
)


def test_v135ay_window_industrial_anchor_continuation_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AYCommercialAerospaceWindowIndustrialAnchorContinuationAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 1
    assert result.summary["covered_window_count"] == 1
    assert result.summary["negative_support_sample_ready_count"] == 1
    assert result.summary["watch_pullback_only_count"] == 1
    assert result.summary["negative_net_flow_count"] == 1
