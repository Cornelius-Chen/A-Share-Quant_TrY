from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kl_a_share_attention_foundation_audit_v1 import (
    V134KLAShareAttentionFoundationAuditV1Analyzer,
)


def test_v134kl_attention_foundation_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KLAShareAttentionFoundationAuditV1Analyzer(repo_root).analyze()

    assert report.summary["attention_registry_count"] == 5
    assert report.summary["hard_attention_role_count"] == 1
    assert report.summary["soft_attention_candidate_count"] == 4


def test_v134kl_attention_foundation_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KLAShareAttentionFoundationAuditV1Analyzer(repo_root).analyze()
    rows = {row["attention_component"]: row for row in report.attention_rows}

    assert rows["attention_registry"]["component_state"] == "materialized_bootstrap"
    assert rows["hard_attention_roles"]["component_state"] == "singleton_hard_case_present"
