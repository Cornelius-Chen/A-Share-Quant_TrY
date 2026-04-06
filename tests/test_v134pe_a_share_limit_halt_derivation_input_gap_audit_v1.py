from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pe_a_share_limit_halt_derivation_input_gap_audit_v1 import (
    V134PEAShareLimitHaltDerivationInputGapAuditV1Analyzer,
)


def test_v134pe_limit_halt_input_gap_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PEAShareLimitHaltDerivationInputGapAuditV1Analyzer(repo_root).analyze()

    assert report.summary["current_surface_field_count"] == 11
    assert report.summary["raw_daily_field_count"] == 12
    assert report.summary["semantic_dependency_field_count"] == 4


def test_v134pe_limit_halt_input_gap_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PEAShareLimitHaltDerivationInputGapAuditV1Analyzer(repo_root).analyze()
    rows = {row["input_class"]: row for row in report.rows}

    assert rows["semantic_dependency_cluster"]["fields"] == "board|is_st|is_suspended|halt_or_suspend_flag"
