from __future__ import annotations

from pathlib import Path

from a_share_quant.strategy.v114y_cpo_free_float_snapshot_collection_v1 import (
    V114YCpoFreeFloatSnapshotCollectionAnalyzer,
    load_json_report,
)


def test_v114y_cpo_free_float_snapshot_collection() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    analyzer = V114YCpoFreeFloatSnapshotCollectionAnalyzer(repo_root=repo_root)

    def fake_fetch(symbol: str) -> dict[str, str]:
        return {
            "股票简称": f"SYM{symbol}",
            "行业": "测试行业",
            "最新": "10.5",
            "总股本": "100000000",
            "流通股": "80000000",
            "总市值": "1050000000",
            "流通市值": "840000000",
        }

    result = analyzer.analyze(
        v112aa_payload=load_json_report(repo_root / "reports/analysis/v112aa_cpo_bounded_cohort_map_v1.json"),
        fetch_symbol_snapshot=fake_fetch,
    )

    assert result.summary["cohort_symbol_count"] == 20
    assert result.summary["collected_symbol_count"] == 20
    assert result.summary["failed_symbol_count"] == 0
    assert result.summary["has_current_float_shares_snapshot"] is True
    assert result.summary["historical_float_time_series_ready_now"] is False
    assert result.collected_rows[0]["float_ratio"] == 0.8
