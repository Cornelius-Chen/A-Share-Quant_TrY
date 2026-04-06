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
class BridgeRule:
    symbol: str
    structure_role: str
    position_state: str
    breakout_state: str
    capital_state: str
    tradability_label: str
    trigger_role: str
    structure_gate_judgement: str
    strict_supervisor_note: str


RULES: tuple[BridgeRule, ...] = (
    BridgeRule(
        symbol="300065",
        structure_role="target_mapping_failure",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        capital_state="headline_only_rebound",
        tradability_label="not_tradable",
        trigger_role="bridge_validation_failure",
        structure_gate_judgement="the_original_mapping_target_failed_so_the_cross_narrative_bridge_cannot_be_treated_as_a_clean_tradeable_leg",
        strict_supervisor_note="海兰信是这扇窗最重要的负证据：桥接叙事在，但原始映射目标本身走弱。",
    ),
    BridgeRule(
        symbol="300342",
        structure_role="formal_chain_partial_bridge",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="bridge_partial_mapping",
        structure_gate_judgement="formal_chain_names_partially_responded_but_not_cleanly_enough_to_upgrade_the_bridge_into_a_primary_leg",
        strict_supervisor_note="天银机电说明跨叙事桥并非完全无效，但正式链响应还不够干净。",
    ),
    BridgeRule(
        symbol="301306",
        structure_role="industrial_outlier",
        position_state="post_hype_pullback",
        breakout_state="platform_breakout",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="outlier_expansion",
        structure_gate_judgement="single_industrial_outliers_can_become_very_strong_without_proving_board_level_bridge_alignment",
        strict_supervisor_note="西测测试是本窗最强 outlier 之一，但不能拿它代替整体桥接成立。",
    ),
    BridgeRule(
        symbol="002565",
        structure_role="concept_bridge_outlier",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        capital_state="headline_only_rebound",
        tradability_label="watch_confirmation_only",
        trigger_role="concept_outlier",
        structure_gate_judgement="concept_names_can_rally_on_bridge_imagination_even_when_formal_mapping_is_not_confirmed",
        strict_supervisor_note="顺灏股份这种概念弹性票更像桥接想象的受益者，不应拿来证明主线成立。",
    ),
    BridgeRule(
        symbol="600135",
        structure_role="emotion_mirror_outlier",
        position_state="post_hype_pullback",
        breakout_state="platform_breakout",
        capital_state="headline_only_rebound",
        tradability_label="watch_confirmation_only",
        trigger_role="emotion_outlier",
        structure_gate_judgement="emotion_mirror_names_can_run_far_ahead_of_the_true_mapping_chain_in_cross_narrative_windows",
        strict_supervisor_note="乐凯胶片更像情绪镜像 outlier，正好用来训练桥接样本里的错配。",
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
    "target_mapping_failure_count",
    "formal_partial_bridge_count",
    "outlier_count",
    "bridge_sample_state",
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

    start_date = "20260305"
    end_date = "20260331"
    output_rows: list[dict[str, Any]] = []
    for rule in RULES:
        bars = by_symbol_bars[rule.symbol]
        window_rows = [row for row in bars if start_date <= row["trade_date"] <= end_date]
        if not window_rows:
            raise ValueError(f"Missing 009 bridge bars for {rule.symbol}")
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
                "sample_window_id": "ca_train_window_009",
                "subwindow_id": "ca009_cross_narrative_bridge_20260305_20260331",
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
            "sample_window_id": "ca_train_window_009",
            "representative_symbol_count": len(output_rows),
            "target_mapping_failure_count": 1,
            "formal_partial_bridge_count": 1,
            "outlier_count": 3,
            "bridge_sample_state": "cross_narrative_bridge_present_but_mapping_misaligned",
            "final_training_admission": "bridge_sample_ready_but_not_final_training",
            "strict_supervisor_conclusion": (
                "Window 009 is a usable bridge sample: the cross-narrative trigger was real and produced selective "
                "A-share responses, but the original mapping target failed and the strongest movers were mostly outliers. "
                "It should teach bridge imagination versus true mapping confirmation, not durable main-leg persistence."
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
        / "commercial_aerospace_202511_202604_window_cross_narrative_bridge_slice_v1.csv"
    )
    summary_path = (
        repo_root
        / "data"
        / "training"
        / "commercial_aerospace_202511_202604_window_cross_narrative_bridge_summary_v1.csv"
    )
    _write_csv(output_path, rows, FIELDNAMES)
    _write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)
    print(f"materialized {len(rows)} rows -> {output_path}")
    print(f"materialized {len(summary_rows)} rows -> {summary_path}")


if __name__ == "__main__":
    main()
