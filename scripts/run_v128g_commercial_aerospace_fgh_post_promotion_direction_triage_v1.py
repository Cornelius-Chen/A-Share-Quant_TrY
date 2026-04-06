from pathlib import Path

from a_share_quant.strategy.v128g_commercial_aerospace_fgh_post_promotion_direction_triage_v1 import (
    V128GCommercialAerospaceFGHPostPromotionDirectionTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128GCommercialAerospaceFGHPostPromotionDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128g_commercial_aerospace_fgh_post_promotion_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
