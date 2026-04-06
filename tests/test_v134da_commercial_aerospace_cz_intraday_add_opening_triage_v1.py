from pathlib import Path

from a_share_quant.strategy.v134cz_commercial_aerospace_intraday_add_opening_checklist_v1 import (
    V134CZCommercialAerospaceIntradayAddOpeningChecklistV1Analyzer,
    write_report as write_checklist_report,
)
from a_share_quant.strategy.v134da_commercial_aerospace_cz_intraday_add_opening_triage_v1 import (
    V134DACommercialAerospaceCZIntradayAddOpeningTriageV1Analyzer,
)


def test_v134da_commercial_aerospace_cz_intraday_add_opening_triage_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checklist = V134CZCommercialAerospaceIntradayAddOpeningChecklistV1Analyzer(repo_root).analyze()
    write_checklist_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134cz_commercial_aerospace_intraday_add_opening_checklist_v1",
        result=checklist,
    )

    result = V134DACommercialAerospaceCZIntradayAddOpeningTriageV1Analyzer(repo_root).analyze()
    assert (
        result.summary["authoritative_status"]
        == "freeze_intraday_add_opening_checklist_and_keep_frontier_deferred_until_explicit_shift"
    )
    assert any(row["component"] == "frontier_opening_now" and row["status"] == "blocked" for row in result.triage_rows)
