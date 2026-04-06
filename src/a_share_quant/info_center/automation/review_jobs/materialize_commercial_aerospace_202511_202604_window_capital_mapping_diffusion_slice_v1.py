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
class DiffusionRule:
    symbol: str
    structure_role: str
    position_state: str
    breakout_state: str
    capital_state: str
    tradability_label: str
    trigger_role: str
    structure_gate_judgement: str
    strict_supervisor_note: str


RULES: tuple[DiffusionRule, ...] = (
    DiffusionRule(
        symbol="002202",
        structure_role="capital_mapping_primary_target_failed",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        capital_state="headline_only_rebound",
        tradability_label="not_tradable",
        trigger_role="capital_diffusion_failure",
        structure_gate_judgement=(
            "the_primary_capital_mapping_name_kept_falling_after_the_story_burst_and_never_established_a_valid_repricing_leg"
        ),
        strict_supervisor_note=(
            "金风科技是这扇窗最重要的负证据：资本映射名单很热，但核心映射票自己持续走弱。"
        ),
    ),
    DiffusionRule(
        symbol="600783",
        structure_role="capital_mapping_secondary_target_failed",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        capital_state="headline_only_rebound",
        tradability_label="not_tradable",
        trigger_role="capital_diffusion_failure",
        structure_gate_judgement=(
            "secondary_capital_mapping_names_only_held_flat_to_down_without_any_clean_breakout_or_capital_confirmation"
        ),
        strict_supervisor_note=(
            "鲁信创投给的只是弱修复，没有结构升级，也没有把名单扩散变成主线确认。"
        ),
    ),
    DiffusionRule(
        symbol="688102",
        structure_role="industrial_material_outlier_failed_to_upgrade",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="local_outlier",
        structure_gate_judgement=(
            "even_the_more_industrial_material_name_only_showed_a_short_local_strength_before_reverting_without_broad_alignment"
        ),
        strict_supervisor_note=(
            "斯瑞新材说明局部工业材料票可以短暂更强，但也不足以证明资本映射扩散成立。"
        ),
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
    "capital_mapping_failure_count",
    "local_outlier_count",
    "board_alignment_state",
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

    start_date = "20260330"
    end_date = "20260402"
    output_rows: list[dict[str, Any]] = []
    for rule in RULES:
        bars = by_symbol_bars[rule.symbol]
        window_rows = [row for row in bars if start_date <= row["trade_date"] <= end_date]
        if not window_rows:
            raise ValueError(f"Missing 006 diffusion bars for {rule.symbol}")
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
                "sample_window_id": "ca_train_window_006",
                "subwindow_id": "ca006_capital_mapping_diffusion_20260330_20260402",
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
            "sample_window_id": "ca_train_window_006",
            "representative_symbol_count": len(output_rows),
            "capital_mapping_failure_count": 2,
            "local_outlier_count": 1,
            "board_alignment_state": "raw_only_post_lockout_alignment_absent",
            "final_training_admission": "negative_sample_ready",
            "strict_supervisor_conclusion": (
                "Window 006 is now a released negative sample: the capital-mapping narrative clearly expanded attention, "
                "but lawful board alignment was absent, the main mapping names failed to establish a repricing leg, and "
                "the few stronger industrial responses remained local outliers. It should train concept-spread-without-structure."
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
        / "commercial_aerospace_202511_202604_window_capital_mapping_diffusion_slice_v1.csv"
    )
    summary_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_capital_mapping_diffusion_summary_v1.csv"
    )
    _write_csv(output_path, rows, FIELDNAMES)
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)
    print(f"materialized {len(rows)} rows -> {output_path}")
    print(f"materialized {len(summary_rows)} rows -> {summary_path}")


if __name__ == "__main__":
    main()
