from pathlib import Path

from a_share_quant.data.tushare_bootstrap import _load_cpo_symbols_from_report, _symbol_to_ts_code


def test_symbol_to_ts_code() -> None:
    assert _symbol_to_ts_code("300308") == "300308.SZ"
    assert _symbol_to_ts_code("688498") == "688498.SH"
    assert _symbol_to_ts_code("830001") == "830001.BJ"


def test_load_cpo_symbols_from_report() -> None:
    symbols = _load_cpo_symbols_from_report(Path("reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json"))
    assert len(symbols) == 20
    assert symbols[0] == "300308"
