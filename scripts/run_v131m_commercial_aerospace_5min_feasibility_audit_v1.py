from pathlib import Path

from a_share_quant.strategy.v131m_commercial_aerospace_5min_feasibility_audit_v1 import (
    V131MCommercialAerospace5MinFeasibilityAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V131MCommercialAerospace5MinFeasibilityAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v131m_commercial_aerospace_5min_feasibility_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
