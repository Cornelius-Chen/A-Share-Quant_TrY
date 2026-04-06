from a_share_quant.strategy.v124k_commercial_aerospace_cross_board_force_protocol_v1 import (
    V124KCommercialAerospaceCrossBoardForceProtocolAnalyzer,
)


def test_v124k_cross_board_force_protocol_promotes_user_named_allies() -> None:
    result = V124KCommercialAerospaceCrossBoardForceProtocolAnalyzer().analyze()

    assert result.summary["cross_board_propulsion_count"] == 3
    assert result.layer_rows[1]["layer_name"] == "layer_2_cross_board_propulsion_allies"
    assert result.layer_rows[1]["members"][0]["symbol"] == "002565"
