from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v134iy_commercial_aerospace_event_attention_heat_proxy_audit_v1 import (
    V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Analyzer,
)


def test_v134iy_event_attention_heat_proxy_audit() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V134IYCommercialAerospaceEventAttentionHeatProxyAuditV1Analyzer(repo_root).analyze()

    assert result.summary["symbol_count"] == 5
    assert result.summary["explicit_heat_anchor_seed_count"] == 1
    assert result.summary["event_backed_heat_carrier_proxy_count"] == 1
    assert result.summary["strongest_soft_heat_proxy_symbol"] == "603601"
    assert result.summary["counterpanel_thickened"] is False

    by_symbol = {row["symbol"]: row for row in result.heat_proxy_rows}
    assert by_symbol["000547"]["heat_proxy_class"] == "explicit_heat_anchor_seed"
    assert by_symbol["603601"]["heat_proxy_class"] == "event_backed_heat_carrier_proxy"
    assert by_symbol["002361"]["heat_proxy_class"] == "crowded_heat_proxy_without_anchor"
