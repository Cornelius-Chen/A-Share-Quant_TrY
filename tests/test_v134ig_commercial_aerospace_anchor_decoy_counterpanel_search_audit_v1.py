from pathlib import Path

from a_share_quant.strategy.v134ig_commercial_aerospace_anchor_decoy_counterpanel_search_audit_v1 import (
    V134IGCommercialAerospaceAnchorDecoyCounterpanelSearchAuditV1Analyzer,
)


def test_v134ig_anchor_decoy_counterpanel_search_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134IGCommercialAerospaceAnchorDecoyCounterpanelSearchAuditV1Analyzer(repo_root).analyze()

    assert report.summary["searched_symbol_count"] == 5
    assert report.summary["current_hard_counterpanel_count"] == 1
    assert report.summary["second_hard_counterpanel_found"] is False
    assert report.summary["soft_decoy_only_candidate_count"] == 2
    rows = {row["symbol"]: row for row in report.search_rows}
    assert rows["000547"]["search_status"] == "current_hard_counterpanel_case"
    assert rows["002361"]["hard_decoy_candidate"] == "soft_only"
    assert rows["300342"]["hard_decoy_candidate"] == "soft_only"
