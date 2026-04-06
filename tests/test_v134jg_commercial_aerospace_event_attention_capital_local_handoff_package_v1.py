from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jg_commercial_aerospace_event_attention_capital_local_handoff_package_v1 import (
    V134JGCommercialAerospaceEventAttentionCapitalLocalHandoffPackageV1Analyzer,
)


def test_v134jg_event_attention_capital_local_handoff_package() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134JGCommercialAerospaceEventAttentionCapitalLocalHandoffPackageV1Analyzer(repo_root).analyze()

    assert result.summary["local_route_mainline_frozen"] is True
    assert result.summary["capital_true_selection_blocked"] is True
    assert result.summary["hard_heat_source_inventory_single_case"] is True
    assert result.summary["future_handoff_ready"] is True

    by_component = {row["component"]: row for row in result.package_rows}
    assert by_component["future_progress_gate"]["status"] == "future_evidence_expansion_only"
