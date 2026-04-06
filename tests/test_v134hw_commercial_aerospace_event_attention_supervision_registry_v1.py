from pathlib import Path

from a_share_quant.strategy.v134hw_commercial_aerospace_event_attention_supervision_registry_v1 import (
    V134HWCommercialAerospaceEventAttentionSupervisionRegistryV1Analyzer,
)


def test_v134hw_event_attention_supervision_registry() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    report = V134HWCommercialAerospaceEventAttentionSupervisionRegistryV1Analyzer(repo_root).analyze()

    assert report.summary["registry_row_count"] == 8
    assert report.summary["event_seed_count"] == 6
    assert report.summary["symbol_role_seed_count"] == 2
    assert report.summary["event_trigger_validity_count"] == 6
    assert report.summary["attention_anchor_count"] == 1
    assert report.summary["attention_decoy_count"] == 1
    assert any(
        row["supervision_label"] == "attention_anchor" and row["symbol"] == "000547"
        for row in report.registry_rows
    )
    assert any(
        row["supervision_label"] == "attention_decoy" and row["symbol"] == "000547"
        for row in report.registry_rows
    )
