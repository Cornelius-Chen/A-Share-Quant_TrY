from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qp_a_share_qo_runtime_stub_lane_direction_triage_v1 import (
    V134QPAShareQORuntimeStubLaneDirectionTriageV1Analyzer,
)


def test_v134qp_runtime_stub_lane_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QPAShareQORuntimeStubLaneDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["lane_row_count"] == 1
    assert report.summary["excluded_row_count"] == 2


def test_v134qp_runtime_stub_lane_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QPAShareQORuntimeStubLaneDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "single_html_article_scheduler_stub_replacement_lane" in rows["runtime_stub_lane"]
