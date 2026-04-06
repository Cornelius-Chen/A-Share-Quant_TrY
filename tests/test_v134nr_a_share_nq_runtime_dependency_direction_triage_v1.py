from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nr_a_share_nq_runtime_dependency_direction_triage_v1 import (
    V134NRAShareNQRuntimeDependencyDirectionTriageV1Analyzer,
)


def test_v134nr_runtime_dependency_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NRAShareNQRuntimeDependencyDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "runtime_activation_depends_on_batch_one_manual_closure_not_scheduler_only"
    )


def test_v134nr_runtime_dependency_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NRAShareNQRuntimeDependencyDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["html_article_runtime"]["direction"].startswith("keep_first_runtime_candidate_blocked")
    assert rows["official_source_runtime"]["direction"].startswith("retain_official_source_runtime")
