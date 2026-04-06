from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qr_a_share_qq_runtime_deployment_direction_triage_v1 import (
    V134QRAShareQQRuntimeDeploymentDirectionTriageV1Analyzer,
)


def test_v134qr_runtime_deployment_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QRAShareQQRuntimeDeploymentDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["candidate_row_count"] == 1
    assert report.summary["promotable_now_count"] == 0


def test_v134qr_runtime_deployment_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QRAShareQQRuntimeDeploymentDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row["direction"] for row in report.triage_rows}

    assert "single_row_candidate_view" in rows["deployment_candidate_view"]
