from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nl_a_share_nk_batch_one_allowlist_direction_triage_v1 import (
    V134NLAShareNKBatchOneAllowlistDirectionTriageV1Analyzer,
)


def test_v134nl_batch_one_allowlist_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NLAShareNKBatchOneAllowlistDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "batch_one_allowlist_should_be_reviewed_by_host_units_not_promoted_yet"
    )


def test_v134nl_batch_one_allowlist_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NLAShareNKBatchOneAllowlistDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["primary_sina_family"]["direction"].startswith("review_finance_sina_com_cn_first")
    assert rows["promotion_gate"]["direction"].startswith("keep_all_batch_one_hosts_not_promoted")
