from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134le_a_share_ld_information_center_completion_direction_triage_v1 import (
    V134LEAShareLDInformationCenterCompletionDirectionTriageV1Analyzer,
)


def test_v134le_information_center_completion_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LEAShareLDInformationCenterCompletionDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["workstream_count"] == 13
    assert (
        report.summary["authoritative_status"]
        == "information_center_foundation_complete_enough_to_freeze_and_review"
    )


def test_v134le_information_center_completion_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LEAShareLDInformationCenterCompletionDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["completion_component"]: row["direction"] for row in report.triage_rows}

    assert directions["backlogs"] == "retain_as_named_backlogs_instead_of_faking_full_promotion"
