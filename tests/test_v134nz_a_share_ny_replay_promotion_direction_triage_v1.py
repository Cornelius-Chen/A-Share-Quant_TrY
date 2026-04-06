from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nz_a_share_ny_replay_promotion_direction_triage_v1 import (
    V134NZAShareNYReplayPromotionDirectionTriageV1Analyzer,
)


def test_v134nz_replay_promotion_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NZAShareNYReplayPromotionDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "replay_promotion_should_shift_from_derivation_blocker_narrative_to_internal_build_precondition_recheck"
    )


def test_v134nz_replay_promotion_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NZAShareNYReplayPromotionDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["index_daily_source_horizon"]["direction"].startswith("retire_old_freeze")
