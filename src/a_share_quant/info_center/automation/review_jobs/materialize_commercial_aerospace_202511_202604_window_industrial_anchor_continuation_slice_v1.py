from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


def _normalize_row(row: dict[str, str]) -> dict[str, str]:
    return {str(key).lstrip("\ufeff"): value for key, value in row.items()}


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [_normalize_row(row) for row in csv.DictReader(handle)]


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


FIELDNAMES = [
    "sample_window_id",
    "subwindow_id",
    "trade_date_start",
    "trade_date_end",
    "symbol",
    "display_name",
    "structure_role",
    "end_return_pct",
    "window_high_vs_pre20_high_pct",
    "volume_ratio_vs_pre5",
    "window_net_mf_amount",
    "position_state",
    "breakout_state",
    "capital_state",
    "tradability_label",
    "trigger_role",
    "structure_gate_judgement",
    "strict_supervisor_note",
]

SUMMARY_FIELDNAMES = [
    "sample_window_id",
    "representative_symbol_count",
    "industrial_anchor_confirmation_state",
    "board_alignment_state",
    "structure_state",
    "final_training_admission",
    "strict_supervisor_conclusion",
]


def materialize(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    bars_path = (
        repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
    )
    flows_path = (
        repo_root / "data" / "raw" / "moneyflow" / "tushare_commercial_aerospace_moneyflow_v1.csv"
    )
    universe_path = repo_root / "data" / "training" / "commercial_aerospace_merged_universe_v1.csv"

    bar_rows = _read_csv(bars_path)
    flow_rows = _read_csv(flows_path)
    universe_rows = {row["symbol"]: row for row in _read_csv(universe_path)}

    symbol = "001208"
    start_date = "20260121"
    end_date = "20260126"

    bars = [row for row in bar_rows if row["symbol"] == symbol]
    if not bars:
        raise ValueError(f"Missing bars for {symbol}")
    bars.sort(key=lambda row: row["trade_date"])
    window_rows = [row for row in bars if start_date <= row["trade_date"] <= end_date]
    if not window_rows:
        raise ValueError(f"Missing 004 continuation bars for {symbol}")
    pre20_rows = [row for row in bars if row["trade_date"] < start_date][-20:]
    pre5_rows = pre20_rows[-5:]

    start_close = float(window_rows[0]["close"])
    end_close = float(window_rows[-1]["close"])
    end_return_pct = ((end_close - start_close) / start_close * 100.0) if start_close else 0.0
    pre20_high = max((float(row["high"]) for row in pre20_rows), default=0.0)
    window_high = max(float(row["high"]) for row in window_rows)
    window_high_vs_pre20_high_pct = ((window_high - pre20_high) / pre20_high * 100.0) if pre20_high else 0.0
    avg_window_volume = sum(float(row["volume"]) for row in window_rows) / len(window_rows)
    avg_pre5_volume = sum(float(row["volume"]) for row in pre5_rows) / len(pre5_rows) if pre5_rows else 0.0
    volume_ratio_vs_pre5 = (avg_window_volume / avg_pre5_volume) if avg_pre5_volume else 0.0
    flow_window_rows = [
        row for row in flow_rows if row["symbol"] == symbol and start_date <= row["trade_date"] <= end_date
    ]
    window_net_mf_amount = sum(float(row.get("net_mf_amount") or 0.0) for row in flow_window_rows)

    output_rows = [
        {
            "sample_window_id": "ca_train_window_004",
            "subwindow_id": "ca004_industrial_anchor_continuation_20260121_20260126",
            "trade_date_start": start_date,
            "trade_date_end": end_date,
            "symbol": symbol,
            "display_name": universe_rows[symbol]["name"],
            "structure_role": "real_industrial_anchor_but_lockout_misaligned_target",
            "end_return_pct": round(end_return_pct, 4),
            "window_high_vs_pre20_high_pct": round(window_high_vs_pre20_high_pct, 4),
            "volume_ratio_vs_pre5": round(volume_ratio_vs_pre5, 4),
            "window_net_mf_amount": round(window_net_mf_amount, 2),
            "position_state": "post_hype_pullback",
            "breakout_state": "not_breakout",
            "capital_state": "moderate_confirmation",
            "tradability_label": "watch_pullback_only",
            "trigger_role": "negative_support",
            "structure_gate_judgement": (
                "the_industrial_anchor_is_real_and_the_target_name_rebounded_locally_but_the_move_stayed_far_below_prior_highs,"
                "_ran_on_subpar_volume_and_finished_with_net_outflow_under_board_lockout_conditions"
            ),
            "strict_supervisor_note": (
                "This window should train true-logic-but-not-tradable behavior: the stock repaired locally, "
                "but the board stayed inside lockout misalignment and never upgraded into a clean continuation."
            ),
        }
    ]

    summary_rows = [
        {
            "sample_window_id": "ca_train_window_004",
            "representative_symbol_count": len(output_rows),
            "industrial_anchor_confirmation_state": "real_industrial_anchor_confirmed",
            "board_alignment_state": "lockout_misaligned_board_response",
            "structure_state": "target_rebounded_but_failed_to_upgrade",
            "final_training_admission": "negative_support_sample_ready",
            "strict_supervisor_conclusion": (
                "Window 004 is now a released negative-support sample: the industrial anchor was real and the target "
                "name did produce a local rebound, but the board stayed misaligned, structure remained below prior highs, "
                "volume did not expand enough, and net flow stayed negative. It should train true-logic-but-not-tradable misalignment."
            ),
        }
    ]
    return output_rows, summary_rows


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    rows, summary_rows = materialize(repo_root)
    output_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_industrial_anchor_continuation_slice_v1.csv"
    )
    summary_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_industrial_anchor_continuation_summary_v1.csv"
    )
    _write_csv(output_path, rows, FIELDNAMES)
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)
    print(f"materialized {len(rows)} rows -> {output_path}")
    print(f"materialized {len(summary_rows)} rows -> {summary_path}")


if __name__ == "__main__":
    main()
