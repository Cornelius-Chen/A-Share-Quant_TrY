from pathlib import Path

from a_share_quant.strategy.v131u_commercial_aerospace_local_5min_override_coverage_audit_v1 import (
    V131UCommercialAerospaceLocal5MinOverrideCoverageAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131UCommercialAerospaceLocal5MinOverrideCoverageAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131u_commercial_aerospace_local_5min_override_coverage_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
