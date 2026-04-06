from pathlib import Path

from a_share_quant.strategy.v134if_commercial_aerospace_ie_second_carrier_direction_triage_v1 import (
    V134IFCommercialAerospaceIESecondCarrierDirectionTriageV1Analyzer,
)


def test_v134if_second_carrier_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134IFCommercialAerospaceIESecondCarrierDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["searched_symbol_count"] == 5
    assert report.summary["second_carrier_case_found"] is False
    directions = {row["search_target"]: row["direction"] for row in report.triage_rows}
    assert directions["second_carrier_case"] == "still_missing_continue_search_without_promoting_true_selection"
