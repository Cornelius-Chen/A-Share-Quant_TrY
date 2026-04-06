from pathlib import Path

from a_share_quant.strategy.v134cn_commercial_aerospace_reduce_handoff_package_v1 import (
    V134CNCommercialAerospaceReduceHandoffPackageV1Analyzer,
    write_report as write_package_report,
)
from a_share_quant.strategy.v134co_commercial_aerospace_cn_reduce_handoff_direction_triage_v1 import (
    V134COCommercialAerospaceCNReduceHandoffDirectionTriageV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    package = V134CNCommercialAerospaceReduceHandoffPackageV1Analyzer(repo_root).analyze()
    write_package_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cn_commercial_aerospace_reduce_handoff_package_v1",
        result=package,
    )
    result = V134COCommercialAerospaceCNReduceHandoffDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134co_commercial_aerospace_cn_reduce_handoff_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
