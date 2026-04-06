from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134px_a_share_replay_shadow_corrected_recheck_audit_v1 import (
    V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer,
)


def test_v134px_shadow_corrected_recheck_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer(repo_root).analyze()

    assert report.summary["base_missing_count"] == 3
    assert report.summary["corrected_missing_count"] == 2
    assert report.summary["boundary_only_residual_count"] == 2
    assert report.summary["calendar_alignment_residual_count"] == 0


def test_v134px_shadow_corrected_recheck_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PXAShareReplayShadowCorrectedRecheckAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["replay_internal_build_recheck"]["component_state"] == (
        "narrowed_to_external_boundary_residuals_under_shadow_overlay"
    )
