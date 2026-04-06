from pathlib import Path

from a_share_quant.strategy.v128d_commercial_aerospace_abc_portability_direction_triage_v1 import (
    V128DCommercialAerospaceABCPortabilityDirectionTriageAnalyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V128DCommercialAerospaceABCPortabilityDirectionTriageAnalyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v128d_commercial_aerospace_abc_portability_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
