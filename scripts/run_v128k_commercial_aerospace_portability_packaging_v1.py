from pathlib import Path

from a_share_quant.strategy.v128k_commercial_aerospace_portability_packaging_v1 import (
    V128KCommercialAerospacePortabilityPackagingAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128KCommercialAerospacePortabilityPackagingAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128k_commercial_aerospace_portability_packaging_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
