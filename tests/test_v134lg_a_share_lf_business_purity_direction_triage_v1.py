from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lg_a_share_lf_business_purity_direction_triage_v1 import (
    V134LGAShareLFBusinessPurityDirectionTriageV1Analyzer,
)


def test_v134lg_business_purity_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LGAShareLFBusinessPurityDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["business_reference_count"] == 82
    assert (
        report.summary["authoritative_status"]
        == "business_reference_and_concept_purity_complete_enough_to_freeze_as_bootstrap"
    )


def test_v134lg_business_purity_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LGAShareLFBusinessPurityDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["residual_backlog"] == "retain_for_future_fundamental_text_and_cross_theme_enrichment"
