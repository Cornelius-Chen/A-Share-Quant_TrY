from pathlib import Path

from a_share_quant.strategy.v126f_commercial_aerospace_zero_trigger_audit_v1 import (
    V126FCommercialAerospaceZeroTriggerAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V126FCommercialAerospaceZeroTriggerAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v126f_commercial_aerospace_zero_trigger_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
