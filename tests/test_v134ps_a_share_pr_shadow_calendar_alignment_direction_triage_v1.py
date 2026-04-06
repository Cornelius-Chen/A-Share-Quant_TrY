from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ps_a_share_pr_shadow_calendar_alignment_direction_triage_v1 import (
    V134PSASharePRShadowCalendarAlignmentDirectionTriageV1Analyzer,
)


def test_v134ps_shadow_calendar_alignment_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PSASharePRShadowCalendarAlignmentDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "shadow_calendar_alignment_should_be_treated_as_auxiliary_shadow_only_candidate_not_timestamp_override"
    )


def test_v134ps_shadow_calendar_alignment_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PSASharePRShadowCalendarAlignmentDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["pti_timestamp_policy"]["direction"].startswith("retain_original_visible_event_timestamp")
    assert rows["shadow_alignment_candidate"]["direction"].startswith("allow_an_auxiliary_effective_trade_date_candidate")
