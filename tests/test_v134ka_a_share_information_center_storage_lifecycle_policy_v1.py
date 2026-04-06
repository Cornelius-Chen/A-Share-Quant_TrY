from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ka_a_share_information_center_storage_lifecycle_policy_v1 import (
    V134KAAshareInformationCenterStorageLifecyclePolicyV1Analyzer,
)


def test_v134ka_storage_lifecycle_policy_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KAAshareInformationCenterStorageLifecyclePolicyV1Analyzer(repo_root).analyze()

    assert report.summary["lifecycle_class_count"] == 10
    assert report.summary["frozen_reference_class_count"] == 3
    assert report.summary["disposable_class_count"] == 3
    assert report.summary["archive_class_count"] >= 4


def test_v134ka_storage_lifecycle_policy_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KAAshareInformationCenterStorageLifecyclePolicyV1Analyzer(repo_root).analyze()
    rows = {row["data_class"]: row for row in report.lifecycle_rows}

    assert rows["raw_intraday_market_data"]["retention_policy"] == "hot_3m|warm_12m|older_cold_archive"
    assert rows["temporary_feature_views_and_join_surfaces"]["default_exit_action"] == "evict"
    assert rows["claim_event_evidence_structures"]["storage_tier"] == "frozen_reference"
