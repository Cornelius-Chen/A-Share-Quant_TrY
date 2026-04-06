from pathlib import Path

from a_share_quant.strategy.v132i_commercial_aerospace_local_1min_rule_false_positive_audit_v1 import (
    V132ICommercialAerospaceLocal1MinRuleFalsePositiveAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132ICommercialAerospaceLocal1MinRuleFalsePositiveAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132i_commercial_aerospace_local_1min_rule_false_positive_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
