from __future__ import annotations

from a_share_quant.backtest.cost_model import CostModel


def test_cost_model_defaults_match_contract_commission() -> None:
    model = CostModel()

    assert model.commission_bps == 1.2
    assert model.stamp_tax_bps == 5.0
    assert model.transfer_fee_bps == 0.1
    assert model.exchange_handling_bps == 0.341
    assert model.regulatory_fee_bps == 0.2
    assert model.min_commission == 5.0


def test_cost_model_from_config_uses_new_default_commission() -> None:
    model = CostModel.from_config({})

    assert model.commission_bps == 1.2
    assert model.stamp_tax_bps == 5.0
    assert model.transfer_fee_bps == 0.1
    assert model.exchange_handling_bps == 0.341
    assert model.regulatory_fee_bps == 0.2
    assert model.min_commission == 5.0


def test_cost_model_calculate_applies_min_commission_and_sell_tax() -> None:
    model = CostModel()

    buy_fee = model.calculate(notional=10_000.0, action="buy")
    sell_fee = model.calculate(notional=10_000.0, action="sell")

    assert buy_fee == 5.641
    assert sell_fee == 10.641
