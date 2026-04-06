from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134iz_commercial_aerospace_iy_heat_proxy_direction_triage_v1 import (
    V134IZCommercialAerospaceIYHeatProxyDirectionTriageV1Analyzer,
)


def test_v134iz_heat_proxy_direction_triage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IZCommercialAerospaceIYHeatProxyDirectionTriageV1Analyzer(repo_root).analyze()

    assert result.summary["strongest_soft_heat_proxy_symbol"] == "603601"
    assert result.summary["counterpanel_thickened"] is False
    assert (
        result.summary["authoritative_status"]
        == "retain_board_local_heat_proxy_layer_and_keep_true_selection_blocked"
    )

    triage_by_component = {row["component"]: row for row in result.triage_rows}
    assert (
        triage_by_component["603601"]["direction"]
        == "retain_as_strongest_soft_heat_carrier_proxy_but_do_not_promote_to_hard_counterpanel_or_true_selection"
    )
