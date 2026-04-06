from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mv_a_share_mu_execution_binding_reaudit_direction_triage_v1 import (
    V134MVAShareMUExecutionBindingReauditDirectionTriageV1Analyzer,
)


def test_v134mv_execution_binding_reaudit_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MVAShareMUExecutionBindingReauditDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "execution_binding_kept_blocked_until_source_gates_and_replay_boundary_residuals_close"
    )


def test_v134mv_execution_binding_reaudit_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MVAShareMUExecutionBindingReauditDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}
    assert rows["replay"]["direction"].startswith("close_boundary_and_calendar_residuals")
