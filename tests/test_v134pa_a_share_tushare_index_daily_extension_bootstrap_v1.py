from __future__ import annotations

import csv
from pathlib import Path


def test_v134pa_tushare_index_daily_extension_raw_exists() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    path = repo_root / "data" / "raw" / "index_daily_bars" / "tushare_index_daily_bars_extension_v1.csv"
    assert path.exists()


def test_v134pa_tushare_index_daily_extension_raw_coverage() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    path = repo_root / "data" / "raw" / "index_daily_bars" / "tushare_index_daily_bars_extension_v1.csv"
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    dates = sorted({row["trade_date"] for row in rows})
    symbols = sorted({row["symbol"] for row in rows})
    assert dates[0] <= "2023-09-22"
    assert dates[-1] >= "2026-03-28"
    assert symbols == ["000001", "000300", "399006"]
