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
class PreheatSliceRule:
    symbol: str
    structure_role: str
    position_state: str
    breakout_state: str
    capital_state: str
    tradability_label: str
    trigger_role: str
    structure_gate_judgement: str
    strict_supervisor_note: str


RULES: tuple[PreheatSliceRule, ...] = (
    PreheatSliceRule(
        symbol="688523",
        structure_role="formal_core_confirmation",
        position_state="low_base",
        breakout_state="platform_breakout",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="preheat_confirmation",
        structure_gate_judgement="formal_name_confirms_the_policy_preheat_was_not_pure_sentiment_but_still_precedes_january_full_ignition",
        strict_supervisor_note="航天环宇是 11 月预热里最该保留的正式组样本，用来证明国家级方向锚不是空概念。",
    ),
    PreheatSliceRule(
        symbol="002792",
        structure_role="seller_shovel_breakout",
        position_state="low_base",
        breakout_state="platform_breakout",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="preheat_confirmation",
        structure_gate_judgement="seller_shovel_name_confirms_early_industrial_mapping_before_the_main_january_board_ignition",
        strict_supervisor_note="通宇通讯说明 11 月预热并非只有情绪镜像，卖铲映射已经开始响应。",
    ),
    PreheatSliceRule(
        symbol="300900",
        structure_role="seller_shovel_supportive_confirmation",
        position_state="low_base",
        breakout_state="trend_continuation",
        capital_state="moderate_confirmation",
        tradability_label="watch_pullback_only",
        trigger_role="preheat_confirmation",
        structure_gate_judgement="manufacturing_support_name_joined_the_preheat_but_strength_stayed_below_later_january_ignition_standard",
        strict_supervisor_note="广联航空给了制造配套的正响应，但强度更适合作为支持样本而不是主代表。",
    ),
    PreheatSliceRule(
        symbol="300102",
        structure_role="emotion_mirror_leader",
        position_state="low_base",
        breakout_state="platform_breakout",
        capital_state="capital_driven_rebound",
        tradability_label="watch_confirmation_only",
        trigger_role="preheat_expansion",
        structure_gate_judgement="emotion_mirror_names_helped_expand_board_attention_but_should_not_be_mistaken_for_the_best_policy_mapping_rep",
        strict_supervisor_note="乾照光电是 11 月窗口里最强的情绪镜像票之一，但不能拿它替代正式映射样本。",
    ),
    PreheatSliceRule(
        symbol="000547",
        structure_role="high_recognition_emotion_confirmation",
        position_state="low_base",
        breakout_state="platform_breakout",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="preheat_expansion",
        structure_gate_judgement="high_recognition_emotion_names_confirmed_breadth_but_the_window_still_belongs_to_policy_preheat_not_full_ignition",
        strict_supervisor_note="航天发展说明板块情绪已经被带起，但这更适合训练预热确认，而不是正式点火模板。",
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
    "formal_or_industrial_confirmation_count",
    "emotion_confirmation_count",
    "positive_preheat_sample_state",
    "final_training_admission",
    "strict_supervisor_conclusion",
]


def materialize(repo_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    structure_path = (
        repo_root
        / "data"
        / "raw"
        / "daily_bars"
        / "tushare_commercial_aerospace_daily_bars_v1.csv"
    )
    moneyflow_path = (
        repo_root
        / "data"
        / "raw"
        / "moneyflow"
        / "tushare_commercial_aerospace_moneyflow_v1.csv"
    )
    universe_path = repo_root / "data" / "training" / "commercial_aerospace_merged_universe_v1.csv"

    bar_rows = _read_csv(structure_path)
    flow_rows = _read_csv(moneyflow_path)
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

    start_date = "20251125"
    end_date = "20251205"
    output_rows: list[dict[str, Any]] = []
    for rule in RULES:
        bars = by_symbol_bars[rule.symbol]
        window_rows = [row for row in bars if start_date <= row["trade_date"] <= end_date]
        if not window_rows:
            raise ValueError(f"Missing 007 preheat bars for {rule.symbol}")
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
                "sample_window_id": "ca_train_window_007",
                "subwindow_id": "ca007_policy_preheat_20251125_20251205",
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
            "sample_window_id": "ca_train_window_007",
            "representative_symbol_count": len(output_rows),
            "formal_or_industrial_confirmation_count": 3,
            "emotion_confirmation_count": 2,
            "positive_preheat_sample_state": "policy_preheat_with_early_ignition_characteristics",
            "final_training_admission": "positive_sample_ready_but_not_final_training",
            "strict_supervisor_conclusion": (
                "Window 007 is no longer policy-only. It already shows broad board confirmation strong enough to count "
                "as an early-ignition-type policy window, with both formal/industrial names and emotion-mirror names "
                "responding together. Still, it should remain below final training because the cleaner January ignition "
                "archetype is handled by window 002."
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
        / "commercial_aerospace_202511_202604_window_preheat_reaction_slice_v1.csv"
    )
    summary_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_preheat_reaction_summary_v1.csv"
    )
    _write_csv(output_path, rows, FIELDNAMES)
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)
    print(f"materialized {len(rows)} rows -> {output_path}")
    print(f"materialized {len(summary_rows)} rows -> {summary_path}")


if __name__ == "__main__":
    main()
