from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134kd_a_share_kc_identity_direction_triage_v1 import (
    V134KDAShareKCIdentityDirectionTriageV1Analyzer,
)


def test_v134kd_identity_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KDAShareKCIdentityDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["materialized_symbol_count"] == 82
    assert (
        report.summary["authoritative_status"]
        == "identity_workstream_complete_enough_to_freeze_and_use_as_foundation_for_taxonomy"
    )


def test_v134kd_identity_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134KDAShareKCIdentityDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["identity_component"]: row["direction"] for row in report.triage_rows}

    assert directions["next_frontier"] == "move_directly_into_taxonomy_foundation_using_materialized_identity_as_input"
