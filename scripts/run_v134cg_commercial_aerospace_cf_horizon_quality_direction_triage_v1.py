from pathlib import Path

from a_share_quant.strategy.v134cf_commercial_aerospace_isolated_sell_side_horizon_quality_audit_v1 import (
    V134CFCommercialAerospaceIsolatedSellSideHorizonQualityAuditV1Analyzer,
    write_report as write_audit_report,
)
from a_share_quant.strategy.v134cg_commercial_aerospace_cf_horizon_quality_direction_triage_v1 import (
    V134CGCommercialAerospaceCFHorizonQualityDirectionTriageV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    audit = V134CFCommercialAerospaceIsolatedSellSideHorizonQualityAuditV1Analyzer(repo_root).analyze()
    write_audit_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cf_commercial_aerospace_isolated_sell_side_horizon_quality_audit_v1",
        result=audit,
    )
    result = V134CGCommercialAerospaceCFHorizonQualityDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cg_commercial_aerospace_cf_horizon_quality_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
