from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pd_a_share_pc_limit_halt_derivation_direction_triage_v1 import (
    V134PDASharePCLimitHaltDerivationDirectionTriageV1Analyzer,
)


def test_v134pd_limit_halt_derivation_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PDASharePCLimitHaltDerivationDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "limit_halt_semantic_materialization_has_reopened_replay_promotion_recheck"
    )


def test_v134pd_limit_halt_derivation_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PDASharePCLimitHaltDerivationDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["limit_halt_derivation"]["direction"].startswith("retire_limit_halt_as_primary_blocker")
