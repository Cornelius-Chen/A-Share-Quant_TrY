from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134py_a_share_px_shadow_corrected_recheck_direction_triage_v1 import (
    V134PYASharePXShadowCorrectedRecheckDirectionTriageV1Analyzer,
)


def test_v134py_shadow_corrected_recheck_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PYASharePXShadowCorrectedRecheckDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "shadow_corrected_recheck_shows_only_external_boundary_residuals_remain_for_replay_internal_build"
    )


def test_v134py_shadow_corrected_recheck_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PYASharePXShadowCorrectedRecheckDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["remaining_residuals"]["direction"] == (
        "treat_remaining_rows_as_external_boundary_residuals_and_do_not_reopen_broad_market_context_rebuild_for_them"
    )
