import json
from pathlib import Path

from a_share_quant.strategy.v134bu_commercial_aerospace_holdings_aware_sell_binding_audit_v1 import (
    V134BUCommercialAerospaceHoldingsAwareSellBindingAuditV1Analyzer,
    write_report as write_audit_report,
)
from a_share_quant.strategy.v134bv_commercial_aerospace_bu_holdings_binding_direction_triage_v1 import (
    V134BVCommercialAerospaceBUHoldingsBindingDirectionTriageV1Analyzer,
)


def test_v134bv_commercial_aerospace_bu_holdings_binding_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit_result = V134BUCommercialAerospaceHoldingsAwareSellBindingAuditV1Analyzer(repo_root).analyze()
    write_audit_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bu_commercial_aerospace_holdings_aware_sell_binding_audit_v1",
        result=audit_result,
    )

    result = V134BVCommercialAerospaceBUHoldingsBindingDirectionTriageV1Analyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "freeze_holdings_mapping_gap_and_build_start_of_day_sell_binding_surface_next"
    )
    assert result.summary["fully_funded_overlap_count"] == 1
    assert result.summary["same_day_primary_collision_count"] == 8

    assert any(
        row["component"] == "same_day_precedence_policy" and row["status"] == "mandatory"
        for row in result.triage_rows
    )
