from pathlib import Path

from a_share_quant.strategy.v131w_commercial_aerospace_local_5min_ambiguous_case_audit_v1 import (
    V131WCommercialAerospaceLocal5MinAmbiguousCaseAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131WCommercialAerospaceLocal5MinAmbiguousCaseAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131w_commercial_aerospace_local_5min_ambiguous_case_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
