from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kf_a_share_ke_taxonomy_direction_triage_v1 import (
    V134KFAShareKETaxonomyDirectionTriageV1Analyzer,
)


def test_v134kf_taxonomy_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KFAShareKETaxonomyDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["concept_covered_symbol_count"] > 0
    assert report.summary["sector_covered_symbol_count"] > 0
    assert (
        report.summary["authoritative_status"]
        == "taxonomy_foundation_complete_enough_to_freeze_and_shift_into_business_reference_population"
    )


def test_v134kf_taxonomy_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KFAShareKETaxonomyDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["taxonomy_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == "move_into_business_reference_population_without_reopening_identity_or_faking_purity_labels"
