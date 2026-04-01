from __future__ import annotations

import csv
import json
from pathlib import Path

from a_share_quant.strategy.v115f_cpo_negative_sample_enrichment_and_action_label_expansion_v1 import (
    V115FCpoNegativeSampleEnrichmentAndActionLabelExpansionAnalyzer,
)


def _write_daily_feed(path: Path) -> None:
    rows = [
        {"symbol": "300502", "trade_date": "2023-05-03", "open": 10, "high": 10.2, "low": 9.9, "close": 10.1},
        {"symbol": "300502", "trade_date": "2023-05-04", "open": 10.1, "high": 10.2, "low": 9.5, "close": 9.7},
        {"symbol": "300502", "trade_date": "2023-05-05", "open": 9.7, "high": 9.8, "low": 9.0, "close": 9.2},
        {"symbol": "300502", "trade_date": "2023-05-08", "open": 9.1, "high": 9.2, "low": 8.7, "close": 8.8},
        {"symbol": "300308", "trade_date": "2023-05-03", "open": 20, "high": 20.2, "low": 19.9, "close": 20.1},
        {"symbol": "300308", "trade_date": "2023-05-04", "open": 20.1, "high": 20.3, "low": 19.6, "close": 19.8},
        {"symbol": "300308", "trade_date": "2023-05-05", "open": 19.7, "high": 19.9, "low": 19.0, "close": 19.1},
        {"symbol": "300308", "trade_date": "2023-05-08", "open": 19.0, "high": 19.1, "low": 18.4, "close": 18.6},
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["symbol", "trade_date", "open", "high", "low", "close"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def test_v115f_negative_enrichment(tmp_path: Path) -> None:
    repo_root = tmp_path
    _write_daily_feed(repo_root / "data" / "raw" / "daily_bars" / "sina_daily_bars_cpo_execution_main_feed_v1.csv")

    v114t_payload = {
        "summary": {"acceptance_posture": "freeze_v114t_cpo_replay_integrity_repair_v1"},
        "executed_order_rows": [
            {"execution_trade_date": "2023-05-03", "symbol": "300502", "quantity": 100, "action": "buy"},
            {"execution_trade_date": "2023-05-03", "symbol": "300308", "quantity": 100, "action": "buy"},
        ],
        "replay_day_rows": [
            {"trade_date": "2023-05-03", "board_context": {"avg_return": -0.04, "breadth": -0.6}},
            {"trade_date": "2023-05-04", "board_context": {"avg_return": -0.05, "breadth": -0.7}},
        ],
    }
    training_rows = [
        {
            "symbol": "300502",
            "trade_date": "2023-05-03",
            "signal_trade_date": "2023-05-03",
            "execution_trade_date": "2023-05-04",
            "execution_open_price": "10.1",
            "action_context": "add_vs_hold",
            "is_repaired_miss_window": "False",
            "fetch_status": "success",
        }
    ]

    analyzer = V115FCpoNegativeSampleEnrichmentAndActionLabelExpansionAnalyzer(repo_root=repo_root)
    report, enriched_rows = analyzer.analyze(v114t_payload=v114t_payload, training_rows=training_rows)

    assert report.summary["acceptance_posture"] == "freeze_v115f_cpo_negative_sample_enrichment_and_action_label_expansion_v1"
    assert report.summary["negative_enrichment_row_count"] >= 1
    assert report.summary["contains_v114s_style_reduce_close_proxy_labels"] is True
    assert any(str(row["action_context"]) in {"reduce_vs_hold", "close_vs_hold"} for row in enriched_rows)
