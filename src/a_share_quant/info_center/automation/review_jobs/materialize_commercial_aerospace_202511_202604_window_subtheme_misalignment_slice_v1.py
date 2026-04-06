from __future__ import annotations

import csv
from dataclasses import dataclass
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


@dataclass(frozen=True, slots=True)
class MisalignmentRule:
    symbol: str
    structure_role: str
    position_state: str
    breakout_state: str
    capital_state: str
    tradability_label: str
    trigger_role: str
    structure_gate_judgement: str
    strict_supervisor_note: str


RULES: tuple[MisalignmentRule, ...] = (
    MisalignmentRule(
        symbol="688270",
        structure_role="target_subtheme_core_but_not_confirmed",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        capital_state="headline_only_rebound",
        tradability_label="not_tradable",
        trigger_role="confirmation_failure",
        structure_gate_judgement="the_target_subtheme_name_itself_failed_to_recover_prior_supply_so_the_logic_cannot_be_promoted",
        strict_supervisor_note="臻镭科技是这扇窗最重要的负证据：子方向逻辑在，但目标核心票自己都没站起来。",
    ),
    MisalignmentRule(
        symbol="300900",
        structure_role="industrial_support_outlier",
        position_state="post_hype_pullback",
        breakout_state="platform_breakout",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="local_outlier",
        structure_gate_judgement="one_industrial_support_name_broke_out_locally_but_could_not_upgrade_a_weak_board_into_a_new_leg",
        strict_supervisor_note="广联航空说明局部强票可以出现，但单个工业配套强点不足以改变整窗失配结论。",
    ),
    MisalignmentRule(
        symbol="300065",
        structure_role="industrial_mapping_repair_only",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="repair",
        structure_gate_judgement="real_mapping_names_showed_repair_but_not_enough_structure_to_count_as_a_new_leg",
        strict_supervisor_note="海兰信给的是修复，不是新腿确认。",
    ),
    MisalignmentRule(
        symbol="600135",
        structure_role="emotion_mirror_outlier",
        position_state="post_hype_pullback",
        breakout_state="platform_breakout",
        capital_state="headline_only_rebound",
        tradability_label="watch_confirmation_only",
        trigger_role="emotion_outlier",
        structure_gate_judgement="emotion_mirror_outliers_can_be_strong_even_when_the_target_subtheme_core_does_not_confirm",
        strict_supervisor_note="乐凯胶片反而更强，恰好说明这扇窗不能拿局部强情绪票替代真正的子方向确认。",
    ),
)


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
    "target_core_confirmation_state",
    "local_outlier_count",
    "broad_alignment_state",
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

    by_symbol_bars: dict[str, list[dict[str, str]]] = {}
    for row in bar_rows:
        by_symbol_bars.setdefault(row["symbol"], []).append(row)
    for rows in by_symbol_bars.values():
        rows.sort(key=lambda row: row["trade_date"])

    by_symbol_flows: dict[str, list[dict[str, str]]] = {}
    for row in flow_rows:
        by_symbol_flows.setdefault(row["symbol"], []).append(row)
    for rows in by_symbol_flows.values():
        rows.sort(key=lambda row: row["trade_date"])

    start_date = "20260306"
    end_date = "20260310"
    output_rows: list[dict[str, Any]] = []
    for rule in RULES:
        bars = by_symbol_bars[rule.symbol]
        window_rows = [row for row in bars if start_date <= row["trade_date"] <= end_date]
        if not window_rows:
            raise ValueError(f"Missing 005 misalignment bars for {rule.symbol}")
        pre20_rows = [row for row in bars if row["trade_date"] < start_date][-20:]
        pre5_rows = pre20_rows[-5:]
        start_close = float(window_rows[0]["close"])
        end_close = float(window_rows[-1]["close"])
        end_return_pct = ((end_close - start_close) / start_close * 100.0) if start_close else 0.0
        pre20_high = max((float(row["high"]) for row in pre20_rows), default=0.0)
        window_high = max(float(row["high"]) for row in window_rows)
        window_high_vs_pre20_high_pct = (
            ((window_high - pre20_high) / pre20_high * 100.0) if pre20_high else 0.0
        )
        avg_window_volume = sum(float(row["volume"]) for row in window_rows) / len(window_rows)
        avg_pre5_volume = (
            sum(float(row["volume"]) for row in pre5_rows) / len(pre5_rows) if pre5_rows else 0.0
        )
        volume_ratio_vs_pre5 = (avg_window_volume / avg_pre5_volume) if avg_pre5_volume else 0.0
        flow_window_rows = [
            row for row in by_symbol_flows.get(rule.symbol, []) if start_date <= row["trade_date"] <= end_date
        ]
        window_net_mf_amount = sum(float(row.get("net_mf_amount") or 0.0) for row in flow_window_rows)
        output_rows.append(
            {
                "sample_window_id": "ca_train_window_005",
                "subwindow_id": "ca005_satellite_internet_reexpansion_20260306_20260310",
                "trade_date_start": start_date,
                "trade_date_end": end_date,
                "symbol": rule.symbol,
                "display_name": universe_rows[rule.symbol]["name"],
                "structure_role": rule.structure_role,
                "end_return_pct": round(end_return_pct, 4),
                "window_high_vs_pre20_high_pct": round(window_high_vs_pre20_high_pct, 4),
                "volume_ratio_vs_pre5": round(volume_ratio_vs_pre5, 4),
                "window_net_mf_amount": round(window_net_mf_amount, 2),
                "position_state": rule.position_state,
                "breakout_state": rule.breakout_state,
                "capital_state": rule.capital_state,
                "tradability_label": rule.tradability_label,
                "trigger_role": rule.trigger_role,
                "structure_gate_judgement": rule.structure_gate_judgement,
                "strict_supervisor_note": rule.strict_supervisor_note,
            }
        )

    summary_rows = [
        {
            "sample_window_id": "ca_train_window_005",
            "representative_symbol_count": len(output_rows),
            "target_core_confirmation_state": "failed_core_confirmation",
            "local_outlier_count": 2,
            "broad_alignment_state": "logic_valid_but_board_not_upgraded",
            "final_training_admission": "negative_sample_ready",
            "strict_supervisor_conclusion": (
                "Window 005 is a clean anti-false-positive sample: the subtheme logic was real, but the target core "
                "name did not confirm, board breadth was too weak, and the few strong names were local outliers rather "
                "than a genuine new leg."
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
        / "commercial_aerospace_202511_202604_window_subtheme_misalignment_slice_v1.csv"
    )
    summary_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_subtheme_misalignment_summary_v1.csv"
    )
    _write_csv(output_path, rows, FIELDNAMES)
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)
    print(f"materialized {len(rows)} rows -> {output_path}")
    print(f"materialized {len(summary_rows)} rows -> {summary_path}")


if __name__ == "__main__":
    main()
