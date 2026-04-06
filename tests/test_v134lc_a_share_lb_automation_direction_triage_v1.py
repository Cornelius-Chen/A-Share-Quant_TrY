from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lc_a_share_lb_automation_direction_triage_v1 import (
    V134LCAShareLBAutomationDirectionTriageV1Analyzer,
)


def test_v134lc_automation_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LCAShareLBAutomationDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["ingest_job_count"] == 3
    assert (
        report.summary["authoritative_status"]
        == "automation_workstream_complete_enough_to_freeze_and_mark_information_center_foundation_complete"
    )


def test_v134lc_automation_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LCAShareLBAutomationDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["automation_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == (
        "freeze_information_center_foundation_as_complete_enough_and_shift_later_into_real_source_activation_or_module_backlog_closure"
    )
