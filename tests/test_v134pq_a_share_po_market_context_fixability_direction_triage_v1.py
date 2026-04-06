from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pq_a_share_po_market_context_fixability_direction_triage_v1 import (
    V134PQASharePOMarketContextFixabilityDirectionTriageV1Analyzer,
)


def test_v134pq_market_context_fixability_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PQASharePOMarketContextFixabilityDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "replay_market_context_residuals_should_split_into_boundary_retention_and_small_internal_calendar_inspection"
    )


def test_v134pq_market_context_fixability_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PQASharePOMarketContextFixabilityDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["external_boundary_residuals"]["direction"].startswith("retain_pre_coverage_residuals")
    assert rows["internal_calendar_alignment_candidate"]["direction"].startswith("inspect_the_single_off_calendar_shadow_slice")
