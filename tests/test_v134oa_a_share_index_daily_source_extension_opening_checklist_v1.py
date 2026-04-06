from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134oa_a_share_index_daily_source_extension_opening_checklist_v1 import (
    V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer,
)


def test_v134oa_index_source_extension_checklist_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer(repo_root).analyze()

    assert report.summary["opening_gate_count"] == 4
    assert report.summary["closed_gate_count"] == 0
    assert report.summary["ready_to_open_now"] is True


def test_v134oa_index_source_extension_checklist_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134OAAShareIndexDailySourceExtensionOpeningChecklistV1Analyzer(repo_root).analyze()

    assert all(row["gate_state"] == "open" for row in report.checklist_rows)
