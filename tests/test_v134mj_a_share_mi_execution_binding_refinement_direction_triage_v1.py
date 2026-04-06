from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mj_a_share_mi_execution_binding_refinement_direction_triage_v1 import (
    V134MJAShareMIExecutionBindingRefinementDirectionTriageV1Analyzer,
)


def test_v134mj_execution_binding_refinement_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MJAShareMIExecutionBindingRefinementDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "execution_binding_kept_blocked_until_refined_source_and_replay_gates_close"
    )


def test_v134mj_execution_binding_refinement_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MJAShareMIExecutionBindingRefinementDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["source_activation"]["direction"].startswith("close_license_review")
