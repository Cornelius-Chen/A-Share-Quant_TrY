from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134qf_a_share_qe_shadow_execution_stub_lane_direction_triage_v1 import (
    V134QFAShareQEShadowExecutionStubLaneDirectionTriageV1Analyzer,
)


def test_v134qf_shadow_execution_stub_lane_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QFAShareQEShadowExecutionStubLaneDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "shadow_execution_stub_replacement_lane_is_ready_for_internal_replay_progress_but_not_for_global_stub_replacement"
    )


def test_v134qf_shadow_execution_stub_lane_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134QFAShareQEShadowExecutionStubLaneDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["base_stub_registry"]["direction"] == (
        "keep_base_stub_unchanged_until_a_later_explicit_promotion_decision_exists"
    )
