from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134me_a_share_live_like_gate_refinement_audit_v1 import (
    V134MEAShareLiveLikeGateRefinementAuditV1Analyzer,
)


def test_v134me_live_like_refinement_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MEAShareLiveLikeGateRefinementAuditV1Analyzer(repo_root).analyze()

    assert report.summary["policy_bound_adapter_count"] == 3
    assert report.summary["materialized_live_like_view_count"] == 2
    assert report.summary["live_like_ready_now"] is False


def test_v134me_live_like_refinement_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MEAShareLiveLikeGateRefinementAuditV1Analyzer(repo_root).analyze()
    rows = {row["gate_component"]: row for row in report.rows}

    assert rows["source_activation"]["component_state"] == "policy_bound_not_activated"
    assert rows["source_activation"]["blocker"] == "selective_activation_shift_required"
