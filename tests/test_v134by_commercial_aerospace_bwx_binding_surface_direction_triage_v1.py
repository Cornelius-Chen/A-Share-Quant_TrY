from pathlib import Path

from a_share_quant.strategy.v134bw_commercial_aerospace_start_of_day_sell_binding_surface_spec_v1 import (
    V134BWCommercialAerospaceStartOfDaySellBindingSurfaceSpecV1Analyzer,
    write_report as write_surface_report,
)
from a_share_quant.strategy.v134bx_commercial_aerospace_same_day_precedence_policy_audit_v1 import (
    V134BXCommercialAerospaceSameDayPrecedencePolicyAuditV1Analyzer,
    write_report as write_precedence_report,
)
from a_share_quant.strategy.v134by_commercial_aerospace_bwx_binding_surface_direction_triage_v1 import (
    V134BYCommercialAerospaceBWXBindingSurfaceDirectionTriageV1Analyzer,
)


def test_v134by_commercial_aerospace_bwx_binding_surface_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    surface = V134BWCommercialAerospaceStartOfDaySellBindingSurfaceSpecV1Analyzer(repo_root).analyze()
    write_surface_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bw_commercial_aerospace_start_of_day_sell_binding_surface_spec_v1",
        result=surface,
    )
    precedence = V134BXCommercialAerospaceSameDayPrecedencePolicyAuditV1Analyzer(repo_root).analyze()
    write_precedence_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134bx_commercial_aerospace_same_day_precedence_policy_audit_v1",
        result=precedence,
    )

    result = V134BYCommercialAerospaceBWXBindingSurfaceDirectionTriageV1Analyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "freeze_binding_surface_spec_and_build_ledger_plus_precedence_before_isolated_lane"
    )
    assert result.summary["must_build_component_count"] == 5
    assert result.summary["collision_session_count"] == 8
