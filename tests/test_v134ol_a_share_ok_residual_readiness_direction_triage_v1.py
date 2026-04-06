from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ol_a_share_ok_residual_readiness_direction_triage_v1 import (
    V134OLAShareOKResidualReadinessDirectionTriageV1Analyzer,
)


def test_v134ol_residual_readiness_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OLAShareOKResidualReadinessDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "residual_backlog_should_now_be_steered_by_group_readiness"
    )


def test_v134ol_residual_readiness_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OLAShareOKResidualReadinessDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["source_internal_manual"]["direction"].startswith("treat_source_manual_fill")
    assert rows["replay_external_source"]["direction"].startswith("treat_replay_external_source")
