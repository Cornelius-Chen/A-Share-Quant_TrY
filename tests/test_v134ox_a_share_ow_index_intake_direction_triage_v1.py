from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ox_a_share_ow_index_intake_direction_triage_v1 import (
    V134OXAShareOWIndexIntakeDirectionTriageV1Analyzer,
)


def test_index_intake_direction_triage_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OXAShareOWIndexIntakeDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["intake_step_count"] == 4
    assert result.summary["closed_step_count"] == 4


def test_index_intake_direction_triage_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134OXAShareOWIndexIntakeDirectionTriageV1Analyzer(repo_root).analyze()

    directions = {row["component"]: row["direction"] for row in result.triage_rows}
    assert directions["source_arrival"] == "wait_for_new_raw_index_source_before_any_reopen"
