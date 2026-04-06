from pathlib import Path

from a_share_quant.strategy.v128f_commercial_aerospace_efg_main_window_downside_promotion_triage_v1 import (
    V128FCommercialAerospaceEFGMainWindowDownsidePromotionTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128FCommercialAerospaceEFGMainWindowDownsidePromotionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128f_commercial_aerospace_efg_main_window_downside_promotion_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
