from pathlib import Path

from a_share_quant.strategy.v128u_commercial_aerospace_intraday_collapse_override_proxy_audit_v1 import (
    V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128UCommercialAerospaceIntradayCollapseOverrideProxyAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128u_commercial_aerospace_intraday_collapse_override_proxy_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
