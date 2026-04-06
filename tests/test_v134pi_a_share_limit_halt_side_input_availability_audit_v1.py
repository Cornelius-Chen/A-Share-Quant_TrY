from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134pi_a_share_limit_halt_side_input_availability_audit_v1 import (
    V134PIAShareLimitHaltSideInputAvailabilityAuditV1Analyzer,
)


def test_v134pi_limit_halt_side_input_availability_summary() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PIAShareLimitHaltSideInputAvailabilityAuditV1Analyzer(repo_root).analyze()

    assert report.summary["retained_family_count"] == 4
    assert report.summary["board_symbol_count"] == 82
    assert report.summary["stk_limit_symbol_count"] == 51


def test_v134pi_limit_halt_side_input_availability_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134PIAShareLimitHaltSideInputAvailabilityAuditV1Analyzer(repo_root).analyze()
    rows = {row["side_input_family"]: row for row in report.rows}

    assert rows["st_proxy_namechange"]["availability_state"] == "retained_sparse"
    assert rows["suspension_records"]["availability_state"] == "retained_sparse"
