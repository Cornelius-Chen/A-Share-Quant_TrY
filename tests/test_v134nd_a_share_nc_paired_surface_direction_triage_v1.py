from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nd_a_share_nc_paired_surface_direction_triage_v1 import (
    V134NDAShareNCPairedSurfaceDirectionTriageV1Analyzer,
)


def test_v134nd_paired_surface_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NDAShareNCPairedSurfaceDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["authoritative_status"] == "paired_surface_candidate_layer_ready_for_promotion_recheck"


def test_v134nd_paired_surface_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NDAShareNCPairedSurfaceDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}
    assert rows["index_daily_extension"]["direction"].startswith("retire_index_daily_as_primary_candidate_gap_blocker")
