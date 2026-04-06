from pathlib import Path

from a_share_quant.strategy.v132p_commercial_aerospace_op_local_1min_shadow_benefit_triage_v1 import (
    V132PCommercialAerospaceOPLocal1MinShadowBenefitTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V132PCommercialAerospaceOPLocal1MinShadowBenefitTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v132p_commercial_aerospace_op_local_1min_shadow_benefit_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
