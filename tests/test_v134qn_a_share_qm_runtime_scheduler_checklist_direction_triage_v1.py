from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qn_a_share_qm_runtime_scheduler_checklist_direction_triage_v1 import (
    V134QNAShareQMRuntimeSchedulerChecklistDirectionTriageV1Analyzer,
)


def test_v134qn_runtime_scheduler_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QNAShareQMRuntimeSchedulerChecklistDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["completed_step_count"] == 3
    assert report.summary["pending_step_count"] == 1


def test_v134qn_runtime_scheduler_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QNAShareQMRuntimeSchedulerChecklistDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "only remaining source-side followthrough step" in rows["remaining_step"]
    assert "outside this lane" in rows["excluded_adapters"]
