from __future__ import annotations

import csv
from pathlib import Path

from a_share_quant.strategy.v122h_cpo_recent_1min_proxy_action_timepoint_label_base_v1 import (
    V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer,
)
from a_share_quant.strategy.v122t_cpo_1min_downside_same_plane_stack_audit_v1 import (
    V122TCpo1MinDownsideSamePlaneStackAuditAnalyzer,
    write_report,
)
from tests.test_v122e_cpo_1min_supportive_quality_discovery_v1 import _write_minimal_supportive_fixture


def _write_recent_daily_context_fixture(tmp_path: Path) -> None:
    reference_dir = tmp_path / "data" / "reference" / "tushare_daily_basic"
    raw_dir = tmp_path / "data" / "raw" / "moneyflow"
    reference_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)

    with (reference_dir / "tushare_cpo_daily_basic_v1.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["trade_date", "symbol", "turnover_rate_f", "volume_ratio"])
        writer.writeheader()
        for trade_date in ["20260401", "20260402"]:
            for symbol in ["300308", "300502"]:
                writer.writerow(
                    {
                        "trade_date": trade_date,
                        "symbol": symbol,
                        "turnover_rate_f": "1.2",
                        "volume_ratio": "1.1",
                    }
                )

    with (raw_dir / "tushare_cpo_moneyflow_v1.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["trade_date", "symbol", "buy_lg_amount", "buy_elg_amount", "sell_lg_amount", "sell_elg_amount"],
        )
        writer.writeheader()
        for trade_date in ["20260401", "20260402"]:
            for symbol in ["300308", "300502"]:
                writer.writerow(
                    {
                        "trade_date": trade_date,
                        "symbol": symbol,
                        "buy_lg_amount": "10",
                        "buy_elg_amount": "5",
                        "sell_lg_amount": "12",
                        "sell_elg_amount": "6",
                    }
                )


def test_v122t_cpo_1min_downside_same_plane_stack_audit(tmp_path: Path) -> None:
    _write_minimal_supportive_fixture(tmp_path)
    _write_recent_daily_context_fixture(tmp_path)
    V122HCpoRecent1MinProxyActionTimepointLabelBaseAnalyzer(repo_root=tmp_path).analyze()

    analyzer = V122TCpo1MinDownsideSamePlaneStackAuditAnalyzer(repo_root=tmp_path)
    result = analyzer.analyze()
    output = write_report(
        reports_dir=tmp_path / "reports" / "analysis",
        report_name="v122t_cpo_1min_downside_same_plane_stack_audit_v1",
        result=result,
    )
    assert output.exists()
    assert result.summary["row_count"] >= 0
