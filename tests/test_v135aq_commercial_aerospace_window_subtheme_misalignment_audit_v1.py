from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v135aq_commercial_aerospace_window_subtheme_misalignment_audit_v1 import (
    V135AQCommercialAerospaceWindowSubthemeMisalignmentAuditV1Analyzer,
)


def test_v135aq_subtheme_misalignment_audit_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V135AQCommercialAerospaceWindowSubthemeMisalignmentAuditV1Analyzer(repo_root).analyze()
    assert result.summary["row_count"] == 4
    assert result.summary["covered_window_count"] == 1
    assert result.summary["not_tradable_count"] == 1
    assert result.summary["watch_only_count"] == 3
    assert result.summary["negative_sample_ready_count"] == 1

