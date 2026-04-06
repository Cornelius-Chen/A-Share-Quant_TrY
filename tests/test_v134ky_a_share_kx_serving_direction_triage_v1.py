from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ky_a_share_kx_serving_direction_triage_v1 import (
    V134KYAShareKXServingDirectionTriageV1Analyzer,
)


def test_v134ky_serving_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KYAShareKXServingDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["research_view_count"] == 6
    assert (
        report.summary["authoritative_status"]
        == "serving_workstream_complete_enough_to_freeze_and_shift_into_governance"
    )


def test_v134ky_serving_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KYAShareKXServingDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["serving_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == (
        "shift_into_governance_workstream_to_add_registry_control_heartbeat_and_promotion_gates"
    )
