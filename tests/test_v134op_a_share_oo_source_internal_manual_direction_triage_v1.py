from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134op_a_share_oo_source_internal_manual_direction_triage_v1 import (
    V134OPAShareOOSourceInternalManualDirectionTriageV1Analyzer,
)


def test_source_internal_manual_direction_triage_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OPAShareOOSourceInternalManualDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["queue_row_count"] == 4
    assert result.summary["ready_primary_review_count"] == 1


def test_source_internal_manual_direction_triage_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OPAShareOOSourceInternalManualDirectionTriageV1Analyzer(repo_root).analyze()

    directions = {row["component"]: row["direction"] for row in result.triage_rows}
    assert directions["primary_review_step"] == "fill_finance_sina_primary_host_family_first"
    assert (
        directions["source_internal_manual_lane"]
        == "treat_operator_queue_and_handoff_package_as_terminal_internal_control_surface"
    )
