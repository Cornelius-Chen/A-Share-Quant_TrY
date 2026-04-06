from pathlib import Path

from a_share_quant.strategy.v128j_commercial_aerospace_ijk_post_primary_direction_triage_v1 import (
    V128JCommercialAerospaceIJKPostPrimaryDirectionTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128JCommercialAerospaceIJKPostPrimaryDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128j_commercial_aerospace_ijk_post_primary_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
