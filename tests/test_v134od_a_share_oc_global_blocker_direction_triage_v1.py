from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134od_a_share_oc_global_blocker_direction_triage_v1 import (
    V134ODAShareOCGlobalBlockerDirectionTriageV1Analyzer,
)


def test_v134od_global_blocker_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ODAShareOCGlobalBlockerDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "information_center_should_now_be_steered_by_dual_stopline_governance"
    )


def test_v134od_global_blocker_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134ODAShareOCGlobalBlockerDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["source_side"]["direction"].startswith("treat_manual_review_record_closure")
    assert rows["replay_side"]["direction"].startswith("retain_replay_promotion")
