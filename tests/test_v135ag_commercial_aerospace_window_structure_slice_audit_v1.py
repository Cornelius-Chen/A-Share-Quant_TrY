from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135ag_commercial_aerospace_window_structure_slice_audit_v1 import (
    V135AGCommercialAerospaceWindowStructureSliceAuditV1Analyzer,
)


def test_v135ag_window_structure_slice_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AGCommercialAerospaceWindowStructureSliceAuditV1Analyzer(repo_root).analyze()

    assert report.summary["structure_row_count"] == 13
    assert report.summary["covered_window_count"] == 3
    assert report.summary["tradable_now_count"] >= 2
    assert report.summary["watch_only_count"] >= 4
    assert report.summary["not_tradable_count"] >= 6
    assert report.summary["negative_sample_ready_count"] == 1


def test_v135ag_window_structure_slice_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V135AGCommercialAerospaceWindowStructureSliceAuditV1Analyzer(repo_root).analyze()

    admissions = {row["sample_window_id"]: row["admission_state"] for row in report.rows}
    assert admissions["ca_train_window_002"] == "hold_until_policy_wording_locked"
    assert admissions["ca_train_window_008"] == "subwindow_ready_but_full_window_not_ready"
    assert admissions["ca_train_window_010"] == "negative_sample_ready"
