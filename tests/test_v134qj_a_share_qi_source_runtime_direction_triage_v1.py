from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qj_a_share_qi_source_runtime_direction_triage_v1 import (
    V134QJAShareQISourceRuntimeDirectionTriageV1Analyzer,
)


def test_v134qj_source_runtime_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QJAShareQISourceRuntimeDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["priority_runtime_candidate_count"] == 1
    assert report.summary["lane_row_count"] == 1
    assert report.summary["unsatisfied_precondition_count"] == 1


def test_v134qj_source_runtime_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QJAShareQISourceRuntimeDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "only_first_runtime_promotion_candidate_lane" in rows["html_article_runtime_lane"]
    assert "stub-replacement lane" in rows["runtime_stub_replacement_lane"]
    assert "close_scheduler_runtime_promotion" in rows["remaining_gate"]
