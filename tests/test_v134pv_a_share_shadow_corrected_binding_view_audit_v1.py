from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pv_a_share_shadow_corrected_binding_view_audit_v1 import (
    V134PVAShareShadowCorrectedBindingViewAuditV1Analyzer,
)


def test_v134pv_shadow_corrected_binding_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PVAShareShadowCorrectedBindingViewAuditV1Analyzer(repo_root).analyze()

    assert report.summary["binding_row_count"] == 17
    assert report.summary["corrected_bound_count"] == 15
    assert report.summary["corrected_missing_count"] == 2
    assert report.summary["corrected_via_effective_trade_date_count"] == 1


def test_v134pv_shadow_corrected_binding_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PVAShareShadowCorrectedBindingViewAuditV1Analyzer(repo_root).analyze()
    rows = {row["component"]: row for row in report.rows}

    assert rows["shadow_corrected_binding_view"]["component_state"] == "materialized_shadow_only_corrected_binding"
