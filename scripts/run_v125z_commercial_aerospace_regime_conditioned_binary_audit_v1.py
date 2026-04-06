from pathlib import Path

from a_share_quant.strategy.v125z_commercial_aerospace_regime_conditioned_binary_audit_v1 import (
    V125ZCommercialAerospaceRegimeConditionedBinaryAuditAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125ZCommercialAerospaceRegimeConditionedBinaryAuditAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v125z_commercial_aerospace_regime_conditioned_binary_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
