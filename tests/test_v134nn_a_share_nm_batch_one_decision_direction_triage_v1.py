from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nn_a_share_nm_batch_one_decision_direction_triage_v1 import (
    V134NNAShareNMBatchOneDecisionDirectionTriageV1Analyzer,
)


def test_v134nn_batch_one_decision_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NNAShareNMBatchOneDecisionDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "batch_one_allowlist_decision_surface_ready_for_manual_review_but_closed"
    )


def test_v134nn_batch_one_decision_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NNAShareNMBatchOneDecisionDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["decision_order"]["direction"].startswith("review_primary_sina_host_first")
    assert rows["promotion_gate"]["direction"].startswith("keep_promotion_closed")
