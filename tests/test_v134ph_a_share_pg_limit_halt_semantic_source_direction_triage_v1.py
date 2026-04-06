from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134ph_a_share_pg_limit_halt_semantic_source_direction_triage_v1 import (
    V134PHASharePGLimitHaltSemanticSourceDirectionTriageV1Analyzer,
)


def test_v134ph_semantic_source_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PHASharePGLimitHaltSemanticSourceDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "semantic_side_input_sources_bootstrapped_for_limit_halt_replay_closure"
    )


def test_v134ph_semantic_source_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PHASharePGLimitHaltSemanticSourceDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["namechange_source"]["direction"].startswith("treat_namechange_as_the_first_retained_st_proxy_source")
