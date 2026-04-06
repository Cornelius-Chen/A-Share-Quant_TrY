from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ql_a_share_qk_runtime_scheduler_direction_triage_v1 import (
    V134QLAShareQKRuntimeSchedulerDirectionTriageV1Analyzer,
)


def test_v134ql_runtime_scheduler_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QLAShareQKRuntimeSchedulerDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["precondition_count"] == 5
    assert report.summary["unsatisfied_count"] == 1


def test_v134ql_runtime_scheduler_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QLAShareQKRuntimeSchedulerDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "only_remaining_source-side runtime blocker" in rows["scheduler_gate"]
    assert "outside_this_followthrough_lane" in rows["excluded_adapters"]
