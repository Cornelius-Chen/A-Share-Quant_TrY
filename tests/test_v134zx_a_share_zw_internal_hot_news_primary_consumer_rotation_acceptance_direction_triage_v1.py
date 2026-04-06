from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134zx_a_share_zw_internal_hot_news_primary_consumer_rotation_acceptance_direction_triage_v1 import (
    V134ZXAShareZWInternalHotNewsPrimaryConsumerRotationAcceptanceDirectionTriageV1Analyzer,
)


def test_v134zx_primary_consumer_rotation_acceptance_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZXAShareZWInternalHotNewsPrimaryConsumerRotationAcceptanceDirectionTriageV1Analyzer(repo_root).analyze()

    assert "authoritative_status" in report.summary
    assert report.summary["acceptance_state"] == "accepted"


def test_v134zx_primary_consumer_rotation_acceptance_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ZXAShareZWInternalHotNewsPrimaryConsumerRotationAcceptanceDirectionTriageV1Analyzer(repo_root).analyze()

    assert len(report.triage_rows) >= 3
