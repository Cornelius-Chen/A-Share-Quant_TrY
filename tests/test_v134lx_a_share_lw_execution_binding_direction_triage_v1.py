from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134lx_a_share_lw_execution_binding_direction_triage_v1 import (
    V134LXAShareLWExecutionBindingDirectionTriageV1Analyzer,
)


def test_v134lx_execution_binding_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LXAShareLWExecutionBindingDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["blocker_count"] == 6
    assert report.summary["authoritative_status"] == "execution_binding_still_blocked_by_named_stack"


def test_v134lx_execution_binding_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LXAShareLWExecutionBindingDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["execution_binding"] == "keep_blocked"
