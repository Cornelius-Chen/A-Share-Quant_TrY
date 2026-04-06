from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ak_commercial_aerospace_window_continuation_breadth_alignment_audit_v1 import (
    V135AKCommercialAerospaceWindowContinuationBreadthAlignmentAuditV1Analyzer,
)


def test_v135ak_continuation_breadth_alignment_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AKCommercialAerospaceWindowContinuationBreadthAlignmentAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 3
    assert result.summary["covered_window_count"] == 1
    assert result.summary["broad_confirmation_real_count"] == 1
    assert result.summary["continuation_not_upgraded_count"] == 1
    assert result.summary["breadth_failed_count"] == 1
    assert result.summary["full_window_hold_count"] == 1

