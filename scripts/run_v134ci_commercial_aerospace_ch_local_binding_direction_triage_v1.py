from pathlib import Path

from a_share_quant.strategy.v134ch_commercial_aerospace_isolated_sell_side_local_binding_attribution_v1 import (
    V134CHCommercialAerospaceIsolatedSellSideLocalBindingAttributionV1Analyzer,
    write_report as write_attr_report,
)
from a_share_quant.strategy.v134ci_commercial_aerospace_ch_local_binding_direction_triage_v1 import (
    V134CICommercialAerospaceCHLocalBindingDirectionTriageV1Analyzer,
    write_report,
)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    attr = V134CHCommercialAerospaceIsolatedSellSideLocalBindingAttributionV1Analyzer(repo_root).analyze()
    write_attr_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ch_commercial_aerospace_isolated_sell_side_local_binding_attribution_v1",
        result=attr,
    )
    result = V134CICommercialAerospaceCHLocalBindingDirectionTriageV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ci_commercial_aerospace_ch_local_binding_direction_triage_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
