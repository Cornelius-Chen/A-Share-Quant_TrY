from pathlib import Path

from a_share_quant.strategy.v134cn_commercial_aerospace_reduce_handoff_package_v1 import (
    V134CNCommercialAerospaceReduceHandoffPackageV1Analyzer,
    write_report as write_package_report,
)
from a_share_quant.strategy.v134co_commercial_aerospace_cn_reduce_handoff_direction_triage_v1 import (
    V134COCommercialAerospaceCNReduceHandoffDirectionTriageV1Analyzer,
)


def test_v134co_commercial_aerospace_cn_reduce_handoff_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    package = V134CNCommercialAerospaceReduceHandoffPackageV1Analyzer(repo_root).analyze()
    write_package_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cn_commercial_aerospace_reduce_handoff_package_v1",
        result=package,
    )

    result = V134COCommercialAerospaceCNReduceHandoffDirectionTriageV1Analyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "freeze_reduce_handoff_package_and_do_not_reopen_reduce_mainline_before_future_frontier_shift"
    )
    assert result.summary["execution_blocker_count"] == 4
