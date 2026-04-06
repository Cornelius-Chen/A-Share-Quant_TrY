from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134mp_a_share_mo_replay_cost_model_direction_triage_v1 import (
    V134MPAShareMOReplayCostModelDirectionTriageV1Analyzer,
)


def test_v134mp_replay_cost_model_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MPAShareMOReplayCostModelDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "replay_cost_model_foundation_complete_enough_to_freeze_until_symbol_binding_shift"
    )


def test_v134mp_replay_cost_model_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134MPAShareMOReplayCostModelDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["cost_model_registry"]["direction"].startswith("freeze_foundation_stub")
