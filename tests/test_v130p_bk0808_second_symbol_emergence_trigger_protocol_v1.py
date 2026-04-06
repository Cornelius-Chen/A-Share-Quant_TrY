from pathlib import Path

from a_share_quant.strategy.v130p_bk0808_second_symbol_emergence_trigger_protocol_v1 import (
    V130PBK0808SecondSymbolEmergenceTriggerProtocolAnalyzer,
)


def test_v130p_bk0808_second_symbol_emergence_trigger_protocol_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130PBK0808SecondSymbolEmergenceTriggerProtocolAnalyzer(repo_root).analyze()

    assert result.summary["nearest_second_symbol_count"] == 1
    assert result.summary["single_symbol_emergence_sufficient_count"] == 1
    assert result.trigger_rows[0]["symbol"] == "600118"
    assert result.trigger_rows[0]["reopen_candidate_if_emerged"] is True
