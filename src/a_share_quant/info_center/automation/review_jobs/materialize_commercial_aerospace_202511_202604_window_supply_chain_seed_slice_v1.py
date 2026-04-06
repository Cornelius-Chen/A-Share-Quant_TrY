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
class SeedRule:
    symbol: str
    structure_role: str
    position_state: str
    breakout_state: str
    capital_state: str
    tradability_label: str
    trigger_role: str
    structure_gate_judgement: str
    strict_supervisor_note: str


RULES: tuple[SeedRule, ...] = (
    SeedRule(
        symbol="300900",
        structure_role="industrial_leader_confirmation",
        position_state="low_base",
        breakout_state="platform_breakout",
        capital_state="capital_driven_rebound",
        tradability_label="tradable_now",
        trigger_role="early_support",
        structure_gate_judgement="industrial_manufacturing_names_confirmed_that_the_supply_chain_seed_had_real_board_strength",
        strict_supervisor_note="广联航空是 001 里最有代表性的工业制造确认样本之一，足够证明这扇窗不是弱 seed。",
    ),
    SeedRule(
        symbol="688523",
        structure_role="formal_chain_support_confirmation",
        position_state="low_base",
        breakout_state="platform_breakout",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="early_support",
        structure_gate_judgement="formal_chain_names_joined_the_seed_window_early_enough_to_validate_real_supply_chain_attention",
        strict_supervisor_note="航天环宇让 001 不再只像概念反应，它补上了正式链条的支持。",
    ),
    SeedRule(
        symbol="301306",
        structure_role="seller_shovel_validation",
        position_state="low_base",
        breakout_state="platform_breakout",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="validation",
        structure_gate_judgement="testing_and_validation_names_helped_turn_the_seed_window_into_a_real_supply_chain_confirmation",
        strict_supervisor_note="西测测试是质量守门人链条的确认样本，说明供应链验证不是空转。",
    ),
    SeedRule(
        symbol="002792",
        structure_role="seller_shovel_supportive_confirmation",
        position_state="low_base",
        breakout_state="trend_continuation",
        capital_state="moderate_confirmation",
        tradability_label="watch_pullback_only",
        trigger_role="validation",
        structure_gate_judgement="supporting_shovel_names_joined_the_seed_window_even_if_their_strength_was_not_the_absolute_front_row",
        strict_supervisor_note="通宇通讯补上了卖铲链条的支持广度。",
    ),
    SeedRule(
        symbol="000547",
        structure_role="emotion_confirmation",
        position_state="low_base",
        breakout_state="platform_breakout",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="breadth_confirmation",
        structure_gate_judgement="emotion_names_confirmed_the_window_had_board_width_not_just_industrial_depth",
        strict_supervisor_note="航天发展说明 001 已经具备明显板块宽度，不只是产业链单点验证。",
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
    "industrial_or_formal_confirmation_count",
    "emotion_confirmation_count",
    "seed_sample_state",
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

    start_date = "20251224"
    end_date = "20251230"
    output_rows: list[dict[str, Any]] = []
    for rule in RULES:
        bars = by_symbol_bars[rule.symbol]
        window_rows = [row for row in bars if start_date <= row["trade_date"] <= end_date]
        if not window_rows:
            raise ValueError(f"Missing 001 seed bars for {rule.symbol}")
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
                "sample_window_id": "ca_train_window_001",
                "subwindow_id": "ca001_supply_chain_seed_20251224_20251230",
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
            "sample_window_id": "ca_train_window_001",
            "representative_symbol_count": len(output_rows),
            "industrial_or_formal_confirmation_count": 4,
            "emotion_confirmation_count": 1,
            "seed_sample_state": "supportive_seed_with_real_board_width",
            "final_training_admission": "positive_support_sample_ready",
            "strict_supervisor_conclusion": (
                "Window 001 is stronger than a preparatory seed only. It already shows a real supportive early-board-width "
                "response across industrial, formal, and emotion names. It should be released as a positive support sample, "
                "but still remain below the cleaner January ignition archetype."
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
        / "commercial_aerospace_202511_202604_window_supply_chain_seed_slice_v1.csv"
    )
    summary_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_supply_chain_seed_summary_v1.csv"
    )
    _write_csv(output_path, rows, FIELDNAMES)
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)
    print(f"materialized {len(rows)} rows -> {output_path}")
    print(f"materialized {len(summary_rows)} rows -> {summary_path}")


if __name__ == "__main__":
    main()
