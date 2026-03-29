from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from a_share_quant.data.free_data_bootstrap import AkshareFreeDataBootstrapper, FreeDataBootstrapConfig


def test_approx_listed_days_uses_list_date_when_available() -> None:
    bootstrapper = object.__new__(AkshareFreeDataBootstrapper)

    assert bootstrapper._approx_listed_days(date(2024, 1, 1), date(2024, 1, 10)) == 9
    assert bootstrapper._approx_listed_days(None, date(2024, 1, 10)) == 0


def test_parse_iso_date_returns_none_for_empty_values() -> None:
    bootstrapper = object.__new__(AkshareFreeDataBootstrapper)

    assert bootstrapper._parse_iso_date("") is None
    assert bootstrapper._parse_iso_date("2024-01-10") == date(2024, 1, 10)


def test_fetch_adjustment_factors_expands_qfq_factor_events_stepwise() -> None:
    class DummyAk:
        @staticmethod
        def stock_zh_a_daily(symbol: str, adjust: str) -> pd.DataFrame:
            assert symbol == "sz000001"
            assert adjust == "qfq-factor"
            return pd.DataFrame(
                [
                    {"date": "2024-06-14", "qfq_factor": "1.20"},
                    {"date": "2024-10-10", "qfq_factor": "1.05"},
                ]
            )

        @staticmethod
        def tool_trade_date_hist_sina() -> pd.DataFrame:
            return pd.DataFrame(
                {
                    "trade_date": [
                        "2024-10-09",
                        "2024-10-10",
                        "2024-10-11",
                    ]
                }
            )

    bootstrapper = object.__new__(AkshareFreeDataBootstrapper)
    bootstrapper.config = FreeDataBootstrapConfig(
        start_date=date(2024, 10, 9),
        end_date=date(2024, 10, 11),
        stock_symbols=["000001"],
        index_symbols=[],
        adjust="qfq",
        pause_seconds=0.0,
        raw_dir=Path("unused"),
        reference_dir=Path("unused"),
        daily_bars_filename="unused.csv",
        index_daily_bars_filename="unused.csv",
        trading_calendar_filename="unused.csv",
        security_master_filename="unused.csv",
        adjustment_factors_filename="unused.csv",
    )
    bootstrapper.ak = DummyAk()
    bootstrapper._security_details_cache = {}
    bootstrapper._adjustment_factor_cache = {}
    bootstrapper._trade_dates_cache = None

    factors = bootstrapper._fetch_adjustment_factors("000001")

    assert factors[date(2024, 10, 9)] == 1.20
    assert factors[date(2024, 10, 10)] == 1.05
    assert factors[date(2024, 10, 11)] == 1.05


def test_from_config_supports_symbol_files_and_deduplicates(tmp_path: Path) -> None:
    stock_file = tmp_path / "stocks.txt"
    stock_file.write_text("# comment\n000001\n600519\n000001\n", encoding="utf-8")
    index_file = tmp_path / "indices.txt"
    index_file.write_text("000300\n399006\n", encoding="utf-8")

    config = FreeDataBootstrapConfig.from_config(
        {
            "time_range": {"start_date": "2024-01-01", "end_date": "2024-12-31"},
            "paths": {"raw_dir": "data/raw", "reference_dir": "data/reference"},
            "provider": {"adjust": "qfq", "pause_seconds": 0.0},
            "universe": {
                "stock_symbols": ["600036"],
                "stock_symbols_file": str(stock_file),
                "index_symbols_file": str(index_file),
            },
            "outputs": {
                "daily_bars_filename": "daily.csv",
                "index_daily_bars_filename": "index.csv",
                "trading_calendar_filename": "calendar.csv",
                "security_master_filename": "master.csv",
                "adjustment_factors_filename": "adj.csv",
            },
        }
    )

    assert config.stock_symbols == ["600036", "000001", "600519"]
    assert config.index_symbols == ["000300", "399006"]
