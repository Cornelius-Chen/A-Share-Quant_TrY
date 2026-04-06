from pathlib import Path

from a_share_quant.strategy.v132e_commercial_aerospace_local_1min_pattern_envelope_audit_v1 import (
    V132ECommercialAerospaceLocal1MinPatternEnvelopeAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132ECommercialAerospaceLocal1MinPatternEnvelopeAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132e_commercial_aerospace_local_1min_pattern_envelope_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
