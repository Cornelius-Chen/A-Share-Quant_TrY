from pathlib import Path

from a_share_quant.strategy.v124r_commercial_aerospace_tushare_feed_bootstrap_v1 import (
    V124RCommercialAerospaceTushareFeedBootstrapReport,
)


def test_v124r_report_shape() -> None:
    result = V124RCommercialAerospaceTushareFeedBootstrapReport(
        summary={"symbol_count": 51},
        output_rows=[{"dataset": "daily_bars", "row_count": 10}],
        interpretation=["ok"],
    )
    payload = result.as_dict()
    assert payload["summary"]["symbol_count"] == 51
    assert payload["output_rows"][0]["dataset"] == "daily_bars"
