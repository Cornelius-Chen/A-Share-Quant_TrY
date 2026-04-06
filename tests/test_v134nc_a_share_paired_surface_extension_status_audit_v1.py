from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nc_a_share_paired_surface_extension_status_audit_v1 import (
    V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer,
)


def test_v134nc_paired_surface_status_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer(repo_root).analyze()

    assert report.summary["index_candidate_cover_count"] == 0
    assert report.summary["limit_halt_candidate_cover_count"] == 14


def test_v134nc_paired_surface_status_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NCASharePairedSurfaceExtensionStatusAuditV1Analyzer(repo_root).analyze()
    rows = {row["paired_surface"]: row for row in report.rows}
    assert rows["index_daily"]["paired_surface_state"] == "candidate_missing"
    assert rows["limit_halt"]["paired_surface_state"] == "candidate_available"
