from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134np_a_share_no_batch_one_closure_direction_triage_v1 import (
    V134NPAShareNOBatchOneClosureDirectionTriageV1Analyzer,
)


def test_v134np_batch_one_closure_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NPAShareNOBatchOneClosureDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "batch_one_closure_depends_on_manual_field_resolution_not_more_design"
    )


def test_v134np_batch_one_closure_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NPAShareNOBatchOneClosureDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["primary_host_family"]["direction"].startswith("resolve_primary_host_family_manual_fields")
    assert rows["promotion_gate"]["direction"].startswith("keep_allowlist_promotion_closed")
