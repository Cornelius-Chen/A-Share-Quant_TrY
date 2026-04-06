from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pj_a_share_pi_limit_halt_side_input_direction_triage_v1 import (
    V134PJASharePILimitHaltSideInputDirectionTriageV1Analyzer,
)


def test_v134pj_limit_halt_side_input_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PJASharePILimitHaltSideInputDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "limit_halt_side_input_families_are_now_present_but_require_semantic_materialization"
    )


def test_v134pj_limit_halt_side_input_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PJASharePILimitHaltSideInputDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["next_step"]["direction"].startswith("build_a_replay-facing_limit_halt_semantic_surface")
