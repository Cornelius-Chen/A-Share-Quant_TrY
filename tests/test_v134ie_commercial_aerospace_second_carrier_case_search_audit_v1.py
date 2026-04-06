from pathlib import Path

from a_share_quant.strategy.v134ie_commercial_aerospace_second_carrier_case_search_audit_v1 import (
    V134IECommercialAerospaceSecondCarrierCaseSearchAuditV1Analyzer,
)


def test_v134ie_second_carrier_case_search_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134IECommercialAerospaceSecondCarrierCaseSearchAuditV1Analyzer(repo_root).analyze()

    assert report.summary["searched_symbol_count"] == 5
    assert report.summary["current_primary_carrier_case_count"] == 1
    assert report.summary["second_carrier_case_found"] is False
    rows = {row["symbol"]: row for row in report.search_rows}
    assert rows["603601"]["carrier_grade"] == "yes_primary"
    assert rows["301306"]["blocking_reason"] == "follow_candidate_not_attention_carrier"
    assert rows["000547"]["blocking_reason"] == "hard_anchor_decoy_case_not_true_selection_candidate"
