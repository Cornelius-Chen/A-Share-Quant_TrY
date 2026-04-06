from pathlib import Path

from a_share_quant.strategy.v134cd_commercial_aerospace_isolated_sell_side_binding_quality_audit_v1 import (
    V134CDCommercialAerospaceIsolatedSellSideBindingQualityAuditV1Analyzer,
    write_report as write_audit_report,
)
from a_share_quant.strategy.v134ce_commercial_aerospace_cd_binding_quality_direction_triage_v1 import (
    V134CECommercialAerospaceCDBindingQualityDirectionTriageV1Analyzer,
)


def test_v134ce_commercial_aerospace_cd_binding_quality_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134CDCommercialAerospaceIsolatedSellSideBindingQualityAuditV1Analyzer(repo_root).analyze()
    write_audit_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cd_commercial_aerospace_isolated_sell_side_binding_quality_audit_v1",
        result=audit,
    )

    result = V134CECommercialAerospaceCDBindingQualityDirectionTriageV1Analyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "retain_isolated_sell_side_binding_surface_and_audit_horizon_quality_next"
    )
    assert result.summary["executed_session_count"] == 12
