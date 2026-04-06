from pathlib import Path

from a_share_quant.strategy.v125m_commercial_aerospace_decisive_event_protocol_v1 import (
    V125MCommercialAerospaceDecisiveEventProtocolAnalyzer,
)


def test_v125m_filters_event_layer_to_decisive_rows() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V125MCommercialAerospaceDecisiveEventProtocolAnalyzer(repo_root).analyze()
    assert result.summary["retained_historical_count"] > 0
    assert result.summary["discarded_historical_count"] > 0
