from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jd_commercial_aerospace_jc_heat_source_direction_triage_v1 import (
    V134JDCommercialAerospaceJCHeatSourceDirectionTriageV1Analyzer,
)


def test_v134jd_heat_source_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134JDCommercialAerospaceJCHeatSourceDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["retained_symbol_named_heat_source_count"] == 1
    assert result.summary["second_symbol_named_heat_source_found"] is False
    assert (
        result.summary["authoritative_status"]
        == "retain_single_symbol_named_heat_source_stopline_and_keep_true_selection_blocked"
    )

    triage_by_component = {row["component"]: row for row in result.triage_rows}
    assert (
        triage_by_component["capital_true_selection"]["direction"]
        == "continue_blocked_because_the_local_event_inventory_itself_does_not_supply_a_second_symbol_named_hard_heat_source"
    )
