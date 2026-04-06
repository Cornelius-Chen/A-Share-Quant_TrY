from pathlib import Path

from a_share_quant.strategy.v134db_commercial_aerospace_intraday_add_prelaunch_status_card_v1 import (
    V134DBCommercialAerospaceIntradayAddPrelaunchStatusCardV1Analyzer,
    write_report as write_status_report,
)
from a_share_quant.strategy.v134dc_commercial_aerospace_db_prelaunch_direction_triage_v1 import (
    V134DCCommercialAerospaceDBPrelaunchDirectionTriageV1Analyzer,
)


def test_v134dc_commercial_aerospace_db_prelaunch_direction_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    status = V134DBCommercialAerospaceIntradayAddPrelaunchStatusCardV1Analyzer(repo_root).analyze()
    write_status_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134db_commercial_aerospace_intraday_add_prelaunch_status_card_v1",
        result=status,
    )

    result = V134DCCommercialAerospaceDBPrelaunchDirectionTriageV1Analyzer(repo_root).analyze()
    assert result.summary["authoritative_status"] == "freeze_intraday_add_prelaunch_status_and_keep_frontier_deferred"
    assert any(
        row["component"] == "intraday_add_opening_now" and row["status"] == "blocked"
        for row in result.triage_rows
    )
