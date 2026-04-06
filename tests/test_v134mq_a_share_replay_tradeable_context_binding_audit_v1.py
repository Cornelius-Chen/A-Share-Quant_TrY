from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mq_a_share_replay_tradeable_context_binding_audit_v1 import (
    V134MQAShareReplayTradeableContextBindingAuditV1Analyzer,
)


def test_v134mq_replay_tradeable_binding_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MQAShareReplayTradeableContextBindingAuditV1Analyzer(repo_root).analyze()

    assert report.summary["binding_row_count"] > 0
    assert report.summary["date_level_bound_count"] == 14
    assert report.summary["missing_date_context_count"] == 3


def test_v134mq_replay_tradeable_binding_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MQAShareReplayTradeableContextBindingAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["tradeable_context_binding"]["component_state"] == "materialized_date_level_binding"
