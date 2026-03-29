from __future__ import annotations

from pathlib import Path

from a_share_quant.data.loaders import (
    load_daily_bars_from_csv,
    load_security_master_from_csv,
    load_trading_calendar_from_csv,
)


def test_load_trading_calendar_from_csv(tmp_path: Path) -> None:
    path = tmp_path / "trading_calendar.csv"
    path.write_text(
        "\n".join(
            [
                "trade_date,is_open,prev_open_date,next_open_date",
                "2024-01-02,true,,2024-01-03",
                "2024-01-03,true,2024-01-02,2024-01-04",
            ]
        ),
        encoding="utf-8",
    )

    entries = load_trading_calendar_from_csv(path)

    assert len(entries) == 2
    assert entries[0].trade_date.isoformat() == "2024-01-02"
    assert entries[0].prev_open_date is None
    assert entries[0].next_open_date is not None
    assert entries[1].prev_open_date is not None


def test_load_security_master_from_csv(tmp_path: Path) -> None:
    path = tmp_path / "security_master.csv"
    path.write_text(
        "\n".join(
            [
                "symbol,name,board,exchange,list_date,delist_date",
                "000001,PingAnBank,Main,SZSE,1991-04-03,",
                "600519,KweichowMoutai,Main,SSE,2001-08-27,",
            ]
        ),
        encoding="utf-8",
    )

    records = load_security_master_from_csv(path)

    assert len(records) == 2
    assert records[0].symbol == "000001"
    assert records[0].list_date is not None
    assert records[1].exchange == "SSE"
    assert records[1].delist_date is None


def test_bootstrap_daily_bars_are_compatible_with_existing_loader() -> None:
    path = Path("data/raw/daily_bars/akshare_daily_bars_bootstrap.csv")
    if not path.exists():
        return

    bars = load_daily_bars_from_csv(path)

    assert bars
    assert bars[0].symbol in {"000001", "000002", "600519"}
