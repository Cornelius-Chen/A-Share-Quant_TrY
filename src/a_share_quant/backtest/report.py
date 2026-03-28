from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from a_share_quant.common.models import BacktestResult


def write_report(
    reports_dir: Path,
    run_id: str,
    result: BacktestResult,
    *,
    extras: dict[str, object] | None = None,
) -> Path:
    """Write a compact JSON report for a backtest run."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{run_id}.json"
    payload = {
        "summary": result.summary,
        "fills": [asdict(fill) for fill in result.fills],
        "closed_trades": [asdict(trade) for trade in result.closed_trades],
        "equity_curve": [asdict(point) for point in result.equity_curve],
        "rejected_signals": result.rejected_signals,
    }
    if extras:
        payload["extras"] = extras
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, default=str)
    return report_path


def write_comparison_report(
    reports_dir: Path,
    run_id: str,
    comparisons: list[dict[str, object]],
    *,
    extras: dict[str, object] | None = None,
) -> Path:
    """Write a comparison report for a strategy suite run."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path = reports_dir / f"{run_id}_comparison.json"
    payload: dict[str, object] = {"comparisons": comparisons}
    if extras:
        payload["extras"] = extras
    with report_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, default=str)
    return report_path
