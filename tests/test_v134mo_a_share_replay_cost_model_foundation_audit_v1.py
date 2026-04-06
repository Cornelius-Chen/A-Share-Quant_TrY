from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mo_a_share_replay_cost_model_foundation_audit_v1 import (
    V134MOAShareReplayCostModelFoundationAuditV1Analyzer,
)


def test_v134mo_replay_cost_model_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MOAShareReplayCostModelFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["cost_model_count"] == 3
    assert report.summary["execution_journal_stub_count"] > 0


def test_v134mo_replay_cost_model_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MOAShareReplayCostModelFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["cost_model_registry"]["component_state"] == "materialized_foundation_stub"
    assert rows["shadow_execution_journal"]["component_state"] == "materialized_stub_surface"
