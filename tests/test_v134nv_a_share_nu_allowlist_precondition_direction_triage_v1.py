from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134nv_a_share_nu_allowlist_precondition_direction_triage_v1 import (
    V134NVAShareNUAllowlistPreconditionDirectionTriageV1Analyzer,
)


def test_v134nv_allowlist_precondition_direction_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NVAShareNUAllowlistPreconditionDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        report.summary["authoritative_status"]
        == "allowlist_promotion_must_wait_for_manual_record_and_runtime_closure"
    )


def test_v134nv_allowlist_precondition_direction_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134NVAShareNUAllowlistPreconditionDirectionTriageV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.triage_rows}

    assert rows["manual_review_records"]["direction"].startswith("fill_standardized_manual_review_records")
    assert rows["promotion_gate"]["direction"].startswith("keep_allowlist_promotion_fully_closed")
