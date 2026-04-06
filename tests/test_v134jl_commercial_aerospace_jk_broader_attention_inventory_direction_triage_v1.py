from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134jl_commercial_aerospace_jk_broader_attention_inventory_direction_triage_v1 import (
    V134JLCommercialAerospaceJKBroaderAttentionInventoryDirectionTriageV1Analyzer,
)


def test_v134jl_broader_attention_inventory_triage_status() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JLCommercialAerospaceJKBroaderAttentionInventoryDirectionTriageV1Analyzer(repo_root).analyze()

    assert report.summary["capital_true_selection_blocked"] is True
    assert report.summary["ready_local_broader_source_count"] == 3
    assert (
        report.summary["authoritative_status"]
        == "retain_broader_attention_evidence_as_protocol_plus_inventory_open_and_fill_it_with_snapshots_and_retained_event_sources_before_any_promotion"
    )


def test_v134jl_triage_rows_cover_expected_components() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134JLCommercialAerospaceJKBroaderAttentionInventoryDirectionTriageV1Analyzer(repo_root).analyze()
    directions = {row["component"]: row["direction"] for row in report.triage_rows}

    assert directions["board_local_event_attention_capital_handoff"] == "retain_as_frozen_read_only_input"
    assert directions["market_snapshot_inventory_v6"] == "promote_as_first_broader_symbol_attention_search_surface"
    assert directions["theme_snapshot_inventory_v7"] == "promote_as_first_broader_heat_proxy_expansion_surface"
    assert directions["decisive_event_registry_v1"] == "promote_as_first_retained_event_source_expansion_surface"
    assert directions["concept_purity_business_reference_layer"] == "keep_deferred_until_future_full_a_share_shift"
    assert directions["capital_true_selection"] == "continue_blocked_during_inventory_stage"
