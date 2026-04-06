from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134oq_a_share_source_internal_manual_handoff_package_v1 import (
    V134OQAShareSourceInternalManualHandoffPackageV1Analyzer,
)


def test_source_internal_manual_handoff_package_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OQAShareSourceInternalManualHandoffPackageV1Analyzer(repo_root).analyze()

    assert result.summary["handoff_row_count"] == 4
    assert result.summary["manual_review_completed_count"] == 4
    assert result.summary["primary_completed_count"] == 1
    assert result.summary["independent_completed_count"] == 2
    assert result.summary["sibling_completed_count"] == 1


def test_source_internal_manual_handoff_package_primary_host() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OQAShareSourceInternalManualHandoffPackageV1Analyzer(repo_root).analyze()

    primary = next(row for row in result.handoff_rows if row["review_priority_order"] == "1")
    assert primary["host"] == "finance.sina.com.cn"
    assert primary["dependency_state"] == "primary_review_completed"
