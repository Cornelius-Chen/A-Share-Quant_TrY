from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134is_commercial_aerospace_outside_named_second_carrier_supervision_audit_v1 import (
    V134ISCommercialAerospaceOutsideNamedSecondCarrierSupervisionAuditV1Analyzer,
)


def test_v134is_outside_named_second_carrier_supervision_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134ISCommercialAerospaceOutsideNamedSecondCarrierSupervisionAuditV1Analyzer(repo_root).analyze()

    assert result.summary["current_primary_case_count"] == 1
    assert result.summary["outside_named_watch_count"] == 1
    assert result.summary["outside_named_watch_has_event_backing"] is False
    assert result.summary["outside_named_watch_local_top_day_count"] == 3

    by_symbol = {row["symbol"]: row for row in result.supervision_rows}
    assert by_symbol["603601"]["supervision_role"] == "current_primary_event_backed_carrier_case"
    assert by_symbol["000738"]["supervision_role"] == "outside_named_local_leadership_second_carrier_watch"
    assert by_symbol["000738"]["event_backing_present"] is False
