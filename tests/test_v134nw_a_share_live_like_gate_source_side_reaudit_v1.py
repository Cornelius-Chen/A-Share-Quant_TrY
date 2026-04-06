from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nw_a_share_live_like_gate_source_side_reaudit_v1 import (
    V134NWAShareLiveLikeGateSourceSideReauditV1Analyzer,
)


def test_v134nw_live_like_source_side_reaudit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NWAShareLiveLikeGateSourceSideReauditV1Analyzer(repo_root).analyze()

    assert report.summary["pending_manual_count"] == 0
    assert report.summary["unsatisfied_precondition_count"] == 1
    assert report.summary["live_like_ready_now"] is False


def test_v134nw_live_like_source_side_reaudit_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NWAShareLiveLikeGateSourceSideReauditV1Analyzer(repo_root).analyze()
    rows = {row["gate_component"]: row for row in report.rows}

    assert rows["source_activation"]["component_state"] == "manual_closure_completed"
    assert rows["source_preconditions"]["component_state"] == "runtime_only_unsatisfied"
