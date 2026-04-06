from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zw_a_share_internal_hot_news_primary_consumer_rotation_acceptance_registry_audit_v1 import (
    V134ZWAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryAuditV1Analyzer,
)


def test_v134zw_primary_consumer_rotation_acceptance_registry_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZWAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryAuditV1Analyzer(repo_root).analyze()

    assert report.summary["acceptance_state"] == "accepted"
    assert report.summary["accepted_top_watch_symbol"]


def test_v134zw_primary_consumer_rotation_acceptance_registry_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZWAShareInternalHotNewsPrimaryConsumerRotationAcceptanceRegistryAuditV1Analyzer(repo_root).analyze()

    assert len(report.rows) >= 3
