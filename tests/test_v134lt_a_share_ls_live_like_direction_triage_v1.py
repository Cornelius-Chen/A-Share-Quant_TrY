from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lt_a_share_ls_live_like_direction_triage_v1 import (
    V134LTAShareLSLiveLikeDirectionTriageV1Analyzer,
)


def test_v134lt_live_like_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LTAShareLSLiveLikeDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["live_like_ready_now"] is False
    assert (
        report.summary["authoritative_status"]
        == "live_like_opening_still_blocked_by_named_prerequisites"
    )


def test_v134lt_live_like_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LTAShareLSLiveLikeDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["live_like_gate"] == "keep_closed"
    assert directions["next_named_gaps"].startswith("close_source_manual_closure_boundary_residuals")
