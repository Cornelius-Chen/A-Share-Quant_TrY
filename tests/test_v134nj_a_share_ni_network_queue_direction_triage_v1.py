from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nj_a_share_ni_network_queue_direction_triage_v1 import (
    V134NJAShareNINetworkQueueDirectionTriageV1Analyzer,
)


def test_v134nj_network_queue_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NJAShareNINetworkQueueDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "network_queue_processing_should_follow_priority_batches_not_flat_activation"
    )


def test_v134nj_network_queue_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NJAShareNINetworkQueueDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["allowlist_batch_one"]["direction"].startswith("review_batch_one_t2_hosts_first")
    assert rows["runtime_other_adapters"]["direction"].startswith("keep_social_column")
