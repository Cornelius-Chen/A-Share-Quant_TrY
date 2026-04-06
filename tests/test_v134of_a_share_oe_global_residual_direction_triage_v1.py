from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134of_a_share_oe_global_residual_direction_triage_v1 import (
    V134OFAShareOEGlobalResidualDirectionTriageV1Analyzer,
)


def test_v134of_global_residual_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OFAShareOEGlobalResidualDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "global_residual_backlog_should_be_worked_by_group_not_as_flat_list"
    )


def test_v134of_global_residual_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OFAShareOEGlobalResidualDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["source_internal_manual"]["direction"].startswith("treat_source_manual_closure")
    assert rows["replay_external_source"]["direction"].startswith("treat_external_index_source_acquisition")
