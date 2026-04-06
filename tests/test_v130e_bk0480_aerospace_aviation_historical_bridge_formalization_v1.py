from pathlib import Path

from a_share_quant.strategy.v130e_bk0480_aerospace_aviation_historical_bridge_formalization_v1 import (
    V130EBK0480AerospaceAviationHistoricalBridgeFormalizationAnalyzer,
)


def test_v130e_bk0480_aerospace_aviation_historical_bridge_formalization_v1() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = V130EBK0480AerospaceAviationHistoricalBridgeFormalizationAnalyzer(repo_root).analyze()

    assert result.summary["target_symbol"] == "600760"
    assert result.summary["harmonization_status"] == "historical_bridge_only"
    assert result.summary["authoritative_status"] == "retain_600760_as_historical_confirmation_bridge_only"
    assert result.summary["second_lane_acceptance_grade"] is False
