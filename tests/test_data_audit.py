from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.data.data_audit import DataAuditConfig, DataPackAuditor


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [",".join(header)]
    lines.extend(",".join(row) for row in rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_data_pack_audit_flags_missing_and_partial_tables(tmp_path: Path) -> None:
    daily_bars = tmp_path / "daily_bars.csv"
    write_csv(
        daily_bars,
        [
            "trade_date",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "turnover",
            "pre_close",
            "adjust_factor",
            "is_st",
            "is_suspended",
            "listed_days",
        ],
        [["2025-01-02", "AAA", "10", "10.5", "9.8", "10.2", "1000", "100000", "9.9", "1.0", "false", "false", "0"]],
    )
    index_bars = tmp_path / "index_daily_bars.csv"
    write_csv(
        index_bars,
        ["trade_date", "symbol", "open", "high", "low", "close", "volume", "turnover", "pre_close"],
        [["2025-01-02", "000300", "100", "101", "99", "100.5", "1000", "100000", "99.5"]],
    )
    security_master = tmp_path / "security_master.csv"
    write_csv(
        security_master,
        ["symbol", "name", "board", "exchange"],
        [["AAA", "Alpha", "Main", "SZSE"]],
    )
    trading_calendar = tmp_path / "trading_calendar.csv"
    write_csv(
        trading_calendar,
        ["trade_date", "is_open", "prev_open_date", "next_open_date"],
        [["2025-01-02", "true", "", "2025-01-03"]],
    )
    sector_mapping = tmp_path / "sector_mapping_daily.csv"
    write_csv(
        sector_mapping,
        ["trade_date", "symbol", "sector_id", "sector_name", "mapping_source", "mapping_version"],
        [["2025-01-02", "AAA", "ALPHA", "Alpha", "akshare_cninfo", "cninfo_bootstrap_v1"]],
    )
    sector_snapshots = tmp_path / "sector_snapshots.csv"
    write_csv(
        sector_snapshots,
        ["trade_date", "sector_id", "sector_name", "persistence", "diffusion", "money_making", "leader_strength", "relative_strength", "activity"],
        [["2025-01-02", "ALPHA", "Alpha", "0.5", "0.5", "0.5", "0.5", "0.5", "0.5"]],
    )
    stock_snapshots = tmp_path / "stock_snapshots.csv"
    write_csv(
        stock_snapshots,
        ["trade_date", "symbol", "sector_id", "sector_name", "expected_upside", "drive_strength", "stability", "liquidity", "late_mover_quality", "resonance"],
        [["2025-01-02", "AAA", "ALPHA", "Alpha", "0.5", "0.5", "0.5", "0.5", "0.5", "0.5"]],
    )
    mainline_windows = tmp_path / "mainline_windows.csv"
    write_csv(
        mainline_windows,
        ["window_id", "symbol", "start_date", "end_date", "capturable_return"],
        [["aaa_1", "AAA", "2025-01-02", "2025-01-03", "0.05"]],
    )

    config = DataAuditConfig(
        protocol_version="protocol_v1.0",
        output_path=tmp_path / "audit.json",
        tables={
            "daily_bars": daily_bars,
            "index_daily_bars": index_bars,
            "security_master": security_master,
            "trading_calendar": trading_calendar,
            "adjustment_factors": tmp_path / "missing_adjustment_factors.csv",
            "sector_mapping_daily": sector_mapping,
            "sector_snapshots": sector_snapshots,
            "stock_snapshots": stock_snapshots,
            "mainline_windows": mainline_windows,
        },
    )

    auditor = DataPackAuditor(config)
    report = auditor.build_report()
    output_path = auditor.write_report(report)

    assert report["summary"]["canonical_missing_count"] == 1
    assert report["tables"]["adjustment_factors"]["status"] == "missing"
    assert report["tables"]["security_master"]["status"] == "bootstrap_partial"
    assert "missing_required_fields:list_date,delist_date" in report["tables"]["security_master"]["errors"]
    assert output_path.exists()
    persisted = json.loads(output_path.read_text(encoding="utf-8"))
    assert persisted["summary"]["baseline_ready"] is False
