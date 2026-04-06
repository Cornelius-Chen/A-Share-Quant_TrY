from pathlib import Path

from a_share_quant.strategy.v132k_commercial_aerospace_local_1min_session_expansion_audit_v1 import (
    V132KCommercialAerospaceLocal1MinSessionExpansionAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132KCommercialAerospaceLocal1MinSessionExpansionAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132k_commercial_aerospace_local_1min_session_expansion_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
