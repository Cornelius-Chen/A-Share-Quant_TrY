from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ov_a_share_ou_source_internal_manual_checklist_direction_triage_v1 import (
    V134OVAShareOUSourceInternalManualChecklistDirectionTriageV1Analyzer,
)


def test_source_internal_manual_checklist_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OVAShareOUSourceInternalManualChecklistDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["checklist_row_count"] == 4
    assert result.summary["stage_1_count"] == 1


def test_source_internal_manual_checklist_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OVAShareOUSourceInternalManualChecklistDirectionTriageV1Analyzer(repo_root).analyze()

    directions = {row["component"]: row["direction"] for row in result.triage_rows}
    assert directions["stage_1"] == "execute_primary_host_family_checklist_first"
