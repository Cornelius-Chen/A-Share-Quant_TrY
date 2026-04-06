from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134la_a_share_kz_governance_direction_triage_v1 import (
    V134LAAShareKZGovernanceDirectionTriageV1Analyzer,
)


def test_v134la_governance_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LAAShareKZGovernanceDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["schema_count"] == 11
    assert (
        report.summary["authoritative_status"]
        == "governance_workstream_complete_enough_to_freeze_and_shift_into_automation"
    )


def test_v134la_governance_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LAAShareKZGovernanceDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["governance_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == (
        "shift_into_automation_workstream_to_materialize_ingest_pipeline_review_retention_and_orchestration_jobs"
    )
