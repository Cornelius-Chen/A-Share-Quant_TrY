from pathlib import Path

from a_share_quant.strategy.v134eh_commercial_aerospace_intraday_add_frontier_opening_v1 import (
    V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Analyzer,
    write_report as write_opening_report,
)
from a_share_quant.strategy.v134ei_commercial_aerospace_eh_add_frontier_direction_triage_v1 import (
    V134EICommercialAerospaceEHAddFrontierDirectionTriageV1Analyzer,
)


def test_v134ei_commercial_aerospace_eh_add_frontier_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    opening = V134EHCommercialAerospaceIntradayAddFrontierOpeningV1Analyzer(repo_root).analyze()
    write_opening_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134eh_commercial_aerospace_intraday_add_frontier_opening_v1",
        result=opening,
    )
    result = V134EICommercialAerospaceEHAddFrontierDirectionTriageV1Analyzer(repo_root).analyze()

    assert (
        result.summary["authoritative_status"]
        == "open_intraday_add_as_supervision_frontier_and_start_registry_bootstrap"
    )
