from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ln_a_share_lm_limit_halt_direction_triage_v1 import (
    V134LNAShareLMLimitHaltDirectionTriageV1Analyzer,
)


def test_v134ln_limit_halt_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LNAShareLMLimitHaltDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["surface_row_count"] == 1936
    assert (
        report.summary["authoritative_status"]
        == "limit_halt_surface_complete_enough_to_freeze_as_bootstrap"
    )


def test_v134ln_limit_halt_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134LNAShareLMLimitHaltDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["residual_backlog"] == (
        "retain_for_future_exchange_precision_and_intraday_limit_state_enrichment"
    )
