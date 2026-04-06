from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134or_a_share_oq_source_internal_manual_handoff_direction_triage_v1 import (
    V134ORAShareOQSourceInternalManualHandoffDirectionTriageV1Analyzer,
)


def test_source_internal_manual_handoff_direction_triage_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ORAShareOQSourceInternalManualHandoffDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["handoff_row_count"] == 4
    assert result.summary["ready_primary_review_count"] == 1


def test_source_internal_manual_handoff_direction_triage_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ORAShareOQSourceInternalManualHandoffDirectionTriageV1Analyzer(repo_root).analyze()

    directions = {row["component"]: row["direction"] for row in result.triage_rows}
    assert directions["primary_host_family"] == "execute_finance_sina_manual_review_first"
    assert (
        directions["handoff_package"]
        == "use_handoff_package_as_the_terminal_source_internal_manual_operator_surface"
    )
