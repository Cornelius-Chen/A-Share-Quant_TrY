from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134on_a_share_om_operator_queue_direction_triage_v1 import (
    V134ONAShareOMOperatorQueueDirectionTriageV1Analyzer,
)


def test_v134on_operator_queue_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ONAShareOMOperatorQueueDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "source_internal_manual_should_now_be_worked_as_operator_queue_not_as_flat_workpack"
    )


def test_v134on_operator_queue_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ONAShareOMOperatorQueueDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["primary_host_family"]["direction"].startswith("start_with_primary_host_family")
    assert rows["queue_governance"]["direction"].startswith("treat_operator_queue")
