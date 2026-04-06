from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pn_a_share_pm_market_context_residual_direction_triage_v1 import (
    V134PNASharePMMarketContextResidualDirectionTriageV1Analyzer,
)


def test_v134pn_market_context_residual_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PNASharePMMarketContextResidualDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "replay_market_context_gap_reduced_to_boundary_and_calendar_residuals"
    )


def test_v134pn_market_context_residual_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PNASharePMMarketContextResidualDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["pre_coverage_residuals"]["direction"].startswith("treat_pre_2024_shadow_slices")
    assert rows["off_calendar_residuals"]["direction"].startswith("treat_off_calendar_shadow_slices")
