from __future__ import annotations

import json
from pathlib import Path

from a_share_quant.audit.run_registry import RunRegistry
from a_share_quant.common.models import BacktestResult


def test_run_registry_writes_metadata(tmp_path: Path) -> None:
    runs_dir = tmp_path / "runs"
    reports_dir = tmp_path / "reports"
    registry = RunRegistry(runs_dir=runs_dir, reports_dir=reports_dir)
    record = registry.create_run(
        config_path=tmp_path / "config.yaml",
        protocol_version="protocol_v1.0",
        run_type="baseline",
        strategy_family="manual_signals",
    )

    result = BacktestResult(
        fills=[],
        closed_trades=[],
        equity_curve=[],
        rejected_signals=[],
        summary={"total_return": 0.0},
    )
    report_path = reports_dir / "report.json"
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path.write_text("{}", encoding="utf-8")

    registry.finalize_run(
        record=record,
        result=result,
        report_path=report_path,
        data_source="sample.csv",
        data_range={"start": "2025-01-01", "end": "2025-01-31"},
        config_paths=["config/demo_backtest.yaml"],
    )

    payload = json.loads(record.metadata_path.read_text(encoding="utf-8"))
    assert payload["status"] == "completed"
    assert payload["report_path"].endswith("report.json")
