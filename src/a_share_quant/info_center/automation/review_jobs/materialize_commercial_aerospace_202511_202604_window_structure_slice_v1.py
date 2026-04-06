from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@dataclass(slots=True)
class StructureSliceConfig:
    sample_window_id: str
    subwindow_id: str
    trade_date_start: str
    trade_date_end: str
    symbol: str
    symbol_role: str
    position_state: str
    breakout_state: str
    breadth_state: str
    capital_state: str
    tradability_label: str
    trigger_role: str
    structure_gate_judgement: str
    final_training_admission: str
    strict_supervisor_note: str


STRUCTURE_SLICE_CONFIGS: tuple[StructureSliceConfig, ...] = (
    StructureSliceConfig(
        sample_window_id="ca_train_window_002",
        subwindow_id="ca002_policy_ignition_core",
        trade_date_start="20260108",
        trade_date_end="20260112",
        symbol="600783",
        symbol_role="概念助推核心",
        position_state="pre_breakout_platform",
        breakout_state="platform_breakout",
        breadth_state="broad_based_rally",
        capital_state="moderate_confirmation",
        tradability_label="tradable_now",
        trigger_role="ignition",
        structure_gate_judgement="policy_plus_capital_mapping_can_ignite_when_board_is_low_and_breadth_expands",
        final_training_admission="hold_until_policy_wording_locked",
        strict_supervisor_note="鲁信创投是概念助推轴最有代表性的点火样本，但不能单靠概念映射完成最终放行。",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_002",
        subwindow_id="ca002_policy_ignition_core",
        trade_date_start="20260108",
        trade_date_end="20260112",
        symbol="600879",
        symbol_role="正式组中军",
        position_state="pre_breakout_platform",
        breakout_state="platform_breakout",
        breadth_state="broad_based_rally",
        capital_state="capital_driven_rebound",
        tradability_label="tradable_now",
        trigger_role="ignition",
        structure_gate_judgement="formal_core_name_confirms_board_ignition_and_validates_breadth",
        final_training_admission="hold_until_policy_wording_locked",
        strict_supervisor_note="航天电子给了正式组中军确认，这类样本比纯概念股更适合训练政策点火后的板块承接。",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_002",
        subwindow_id="ca002_policy_ignition_core",
        trade_date_start="20260108",
        trade_date_end="20260112",
        symbol="001208",
        symbol_role="卖铲人强化",
        position_state="main_uptrend",
        breakout_state="trend_continuation",
        breadth_state="broad_based_rally",
        capital_state="moderate_confirmation",
        tradability_label="watch_pullback_only",
        trigger_role="confirmation",
        structure_gate_judgement="industrial_mapping_strength_exists_but_entry_quality_is_weaker_after_prior_seed_run",
        final_training_admission="hold_until_policy_wording_locked",
        strict_supervisor_note="华菱线缆更像卖铲人强化样本，不宜误当成最优低位首发票。",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_008",
        subwindow_id="ca008_forum_cluster_20251222_20251226",
        trade_date_start="20251222",
        trade_date_end="20251226",
        symbol="688568",
        symbol_role="卫星数据应用正式组",
        position_state="pre_breakout_platform",
        breakout_state="platform_breakout",
        breadth_state="selective_subtheme_rally",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="diffusion",
        structure_gate_judgement="conference_density_can_expand_subtheme_attention_without_upgrading_to_full_board_ignition",
        final_training_admission="subwindow_ready_but_full_window_not_ready",
        strict_supervisor_note="中科星图说明会议链能带来扩散，但还不足以单独定义全面主升。",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_008",
        subwindow_id="ca008_forum_cluster_20251222_20251226",
        trade_date_start="20251222",
        trade_date_end="20251226",
        symbol="300045",
        symbol_role="卫星通信活跃前排",
        position_state="pre_breakout_platform",
        breakout_state="platform_breakout",
        breadth_state="selective_subtheme_rally",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="diffusion",
        structure_gate_judgement="meeting_chain_can_create_local_breakout_but_still_needs_board_breadth_confirmation",
        final_training_admission="subwindow_ready_but_full_window_not_ready",
        strict_supervisor_note="华力创通有局部突破，但仍然属于结构性响应，不可直接升格成板块点火模板。",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_008",
        subwindow_id="ca008_forum_cluster_20251222_20251226",
        trade_date_start="20251222",
        trade_date_end="20251226",
        symbol="688066",
        symbol_role="遥感服务正式组",
        position_state="pre_breakout_platform",
        breakout_state="not_breakout",
        breadth_state="selective_subtheme_rally",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="diffusion",
        structure_gate_judgement="conference_chain_supports_selective_followthrough_even_when_some_formal_names_do_not_clear_prior_supply",
        final_training_admission="subwindow_ready_but_full_window_not_ready",
        strict_supervisor_note="航天宏图是会议链的好反例：方向在，但并非所有正式组都形成有效突破。",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_008",
        subwindow_id="ca008_forum_cluster_20251222_20251226",
        trade_date_start="20251222",
        trade_date_end="20251226",
        symbol="002465",
        symbol_role="通信导航配套",
        position_state="pre_breakout_platform",
        breakout_state="platform_breakout",
        breadth_state="selective_subtheme_rally",
        capital_state="moderate_confirmation",
        tradability_label="watch_confirmation_only",
        trigger_role="diffusion",
        structure_gate_judgement="conference_chain_can_support_a_moderate_subtheme_expansion_without_broad_board_reopening",
        final_training_admission="subwindow_ready_but_full_window_not_ready",
        strict_supervisor_note="海格通信说明会议链更像子方向扩散，不宜误训练成全面板块重估。",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_008",
        subwindow_id="ca008_feb_followthrough_20260203_20260213",
        trade_date_start="20260203",
        trade_date_end="20260213",
        symbol="688568",
        symbol_role="feb_followthrough_core_data_app",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        breadth_state="failed_diffusion",
        capital_state="headline_only_rebound",
        tradability_label="not_tradable",
        trigger_role="confirmation",
        structure_gate_judgement="conference_chain_followthrough_failed_to_hold_even_core_data_application_names",
        final_training_admission="subwindow_ready_but_full_window_not_ready",
        strict_supervisor_note="February followthrough failed to hold even a core conference-chain name, so the meeting chain still cannot be promoted to a full-window pass.",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_008",
        subwindow_id="ca008_feb_followthrough_20260203_20260213",
        trade_date_start="20260203",
        trade_date_end="20260213",
        symbol="688066",
        symbol_role="feb_followthrough_remote_sensing_service",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        breadth_state="failed_diffusion",
        capital_state="headline_only_rebound",
        tradability_label="not_tradable",
        trigger_role="confirmation",
        structure_gate_judgement="conference_chain_followthrough_did_not_upgrade_remote_sensing_service_names_into_a_new_tradable_leg",
        final_training_admission="subwindow_ready_but_full_window_not_ready",
        strict_supervisor_note="February followthrough in 航天宏图 stayed a weak repair only and is not enough for a full meeting-chain promotion.",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_008",
        subwindow_id="ca008_feb_followthrough_20260203_20260213",
        trade_date_start="20260203",
        trade_date_end="20260213",
        symbol="002465",
        symbol_role="feb_followthrough_comm_nav_support",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        breadth_state="failed_diffusion",
        capital_state="headline_only_rebound",
        tradability_label="not_tradable",
        trigger_role="confirmation",
        structure_gate_judgement="conference_chain_followthrough_faded_into_selective_weak_repair_without_clean_capital_support",
        final_training_admission="subwindow_ready_but_full_window_not_ready",
        strict_supervisor_note="February followthrough in 海格通信 confirms that meeting density alone does not guarantee sustained capital-led continuation.",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_010",
        subwindow_id="ca010_launch_cluster_20260313_20260318",
        trade_date_start="20260313",
        trade_date_end="20260318",
        symbol="600118",
        symbol_role="整机核心龙头",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        breadth_state="failed_diffusion",
        capital_state="headline_only_rebound",
        tradability_label="not_tradable",
        trigger_role="confirmation",
        structure_gate_judgement="official_launch_milestone_confirms_industry_progress_but_does_not_reopen_board_tradability",
        final_training_admission="negative_sample_ready",
        strict_supervisor_note="中国卫星在正式发射节点仍未恢复有效结构，是最关键的负样本之一。",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_010",
        subwindow_id="ca010_launch_cluster_20260313_20260318",
        trade_date_start="20260313",
        trade_date_end="20260318",
        symbol="600879",
        symbol_role="正式组核心配套",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        breadth_state="failed_diffusion",
        capital_state="headline_only_rebound",
        tradability_label="not_tradable",
        trigger_role="confirmation",
        structure_gate_judgement="repeated_launch_progress_without_board_alignment_should_train_non_promotion_not_chasing",
        final_training_admission="negative_sample_ready",
        strict_supervisor_note="航天电子给了同样的负反馈，说明不是单一个股问题，而是板块未被重新点火。",
    ),
    StructureSliceConfig(
        sample_window_id="ca_train_window_010",
        subwindow_id="ca010_launch_cluster_20260313_20260318",
        trade_date_start="20260313",
        trade_date_end="20260318",
        symbol="688568",
        symbol_role="卫星应用跟随",
        position_state="post_hype_pullback",
        breakout_state="not_breakout",
        breadth_state="failed_diffusion",
        capital_state="headline_only_rebound",
        tradability_label="not_tradable",
        trigger_role="confirmation",
        structure_gate_judgement="launch_news_can_stay_as_background_progress_when_core_plus_follower_names_do_not_expand_together",
        final_training_admission="negative_sample_ready",
        strict_supervisor_note="中科星图补足了跟随维度：跟随也没开，说明这批发射里程碑更像背景持续而非新腿。",
    ),
)


@dataclass(slots=True)
class MaterializedCommercialAerospaceWindowStructureSliceV1:
    structure_rows: list[dict[str, Any]]
    summary_rows: list[dict[str, Any]]


class MaterializeCommercialAerospaceWindowStructureSliceV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.bars_path = (
            repo_root / "data" / "raw" / "daily_bars" / "tushare_commercial_aerospace_daily_bars_v1.csv"
        )
        self.moneyflow_path = (
            repo_root / "data" / "raw" / "moneyflow" / "tushare_commercial_aerospace_moneyflow_v1.csv"
        )
        self.universe_path = repo_root / "data" / "training" / "commercial_aerospace_merged_universe_v1.csv"
        self.output_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_structure_slice_v1.csv"
        )
        self.summary_path = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_202511_202604_window_training_admission_summary_v1.csv"
        )

    def _load_name_map(self) -> dict[str, str]:
        name_map: dict[str, str] = {}
        for row in _read_csv(self.universe_path):
            name_map[row["symbol"].zfill(6)] = row["name"]
        return name_map

    def _load_bars(self, symbols: set[str]) -> dict[str, list[dict[str, Any]]]:
        bars: dict[str, list[dict[str, Any]]] = defaultdict(list)
        with self.bars_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                symbol = row["symbol"].zfill(6)
                if symbol not in symbols:
                    continue
                bars[symbol].append(
                    {
                        "trade_date": row["trade_date"],
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "pct_chg": float(row["pct_chg"]),
                        "volume": float(row["volume"]),
                    }
                )
        for symbol_rows in bars.values():
            symbol_rows.sort(key=lambda item: item["trade_date"])
        return bars

    def _load_moneyflow(self, symbols: set[str]) -> dict[str, dict[str, float]]:
        moneyflow: dict[str, dict[str, float]] = defaultdict(dict)
        with self.moneyflow_path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                symbol = row["symbol"].zfill(6)
                if symbol not in symbols:
                    continue
                moneyflow[symbol][row["trade_date"]] = float(row["net_mf_amount"])
        return moneyflow

    def _compute_metrics(
        self,
        *,
        rows: list[dict[str, Any]],
        moneyflow_rows: dict[str, float],
        trade_date_start: str,
        trade_date_end: str,
    ) -> dict[str, Any]:
        idx_start = next(
            (index for index, row in enumerate(rows) if row["trade_date"] >= trade_date_start),
            None,
        )
        idx_end = max(index for index, row in enumerate(rows) if row["trade_date"] <= trade_date_end)
        if idx_start is None:
            raise ValueError(f"missing trade window start {trade_date_start}")
        window_rows = rows[idx_start : idx_end + 1]
        pre_window_rows = rows[max(0, idx_start - 20) : idx_start]
        pre5_rows = rows[max(0, idx_start - 5) : idx_start]
        start_close = window_rows[0]["close"]
        end_close = window_rows[-1]["close"]
        window_high = max(row["high"] for row in window_rows)
        window_low = min(row["low"] for row in window_rows)
        pre20_high = max(row["high"] for row in pre_window_rows) if pre_window_rows else window_high
        pre20_low = min(row["low"] for row in pre_window_rows) if pre_window_rows else window_low
        pre5_avg_volume = mean(row["volume"] for row in pre5_rows) if pre5_rows else mean(row["volume"] for row in window_rows)
        window_avg_volume = mean(row["volume"] for row in window_rows)
        return {
            "start_trade_date": window_rows[0]["trade_date"],
            "end_trade_date": window_rows[-1]["trade_date"],
            "start_close": round(start_close, 4),
            "end_close": round(end_close, 4),
            "end_return_pct": round((end_close / start_close - 1.0) * 100.0, 4),
            "window_high": round(window_high, 4),
            "window_low": round(window_low, 4),
            "pre20_high": round(pre20_high, 4),
            "pre20_low": round(pre20_low, 4),
            "window_high_vs_pre20_high_pct": round((window_high / pre20_high - 1.0) * 100.0, 4),
            "window_avg_volume": round(window_avg_volume, 4),
            "pre5_avg_volume": round(pre5_avg_volume, 4),
            "volume_ratio_vs_pre5": round(window_avg_volume / pre5_avg_volume, 4),
            "up_day_count": sum(1 for row in window_rows if row["pct_chg"] > 0.0),
            "window_net_mf_amount": round(sum(moneyflow_rows.get(row["trade_date"], 0.0) for row in window_rows), 4),
        }

    def materialize(self) -> MaterializedCommercialAerospaceWindowStructureSliceV1:
        symbol_set = {config.symbol for config in STRUCTURE_SLICE_CONFIGS}
        name_map = self._load_name_map()
        bars = self._load_bars(symbol_set)
        moneyflow = self._load_moneyflow(symbol_set)

        structure_rows: list[dict[str, Any]] = []
        for config in STRUCTURE_SLICE_CONFIGS:
            metrics = self._compute_metrics(
                rows=bars[config.symbol],
                moneyflow_rows=moneyflow.get(config.symbol, {}),
                trade_date_start=config.trade_date_start,
                trade_date_end=config.trade_date_end,
            )
            structure_rows.append(
                {
                    "sample_window_id": config.sample_window_id,
                    "subwindow_id": config.subwindow_id,
                    "trade_date_start": config.trade_date_start,
                    "trade_date_end": config.trade_date_end,
                    "symbol": config.symbol,
                    "display_name": name_map.get(config.symbol, config.symbol),
                    "symbol_role": config.symbol_role,
                    **metrics,
                    "position_state": config.position_state,
                    "breakout_state": config.breakout_state,
                    "breadth_state": config.breadth_state,
                    "capital_state": config.capital_state,
                    "tradability_label": config.tradability_label,
                    "trigger_role": config.trigger_role,
                    "structure_gate_judgement": config.structure_gate_judgement,
                    "final_training_admission": config.final_training_admission,
                    "strict_supervisor_note": config.strict_supervisor_note,
                }
            )

        grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in structure_rows:
            grouped_rows[row["sample_window_id"]].append(row)

        summary_rows: list[dict[str, Any]] = []
        for sample_window_id, rows in sorted(grouped_rows.items()):
            admissions = {row["final_training_admission"] for row in rows}
            if admissions == {"negative_sample_ready"}:
                admission_state = "negative_sample_ready"
                strict_supervisor_conclusion = "This launch cluster is strong enough for a negative sample: official milestones did not reopen the board."
            elif admissions == {"subwindow_ready_but_full_window_not_ready"}:
                admission_state = "subwindow_ready_but_full_window_not_ready"
                strict_supervisor_conclusion = "The forum cluster can be used as a selective-diffusion subwindow, but the full meeting chain is not ready for final training."
            else:
                admission_state = "hold_until_policy_wording_locked"
                strict_supervisor_conclusion = "The ignition structure is visible, but the January policy wording must still be locked before final training admission."
            summary_rows.append(
                {
                    "sample_window_id": sample_window_id,
                    "representative_symbol_count": len(rows),
                    "tradable_now_count": sum(1 for row in rows if row["tradability_label"] == "tradable_now"),
                    "watch_only_count": sum(1 for row in rows if row["tradability_label"] in {"watch_pullback_only", "watch_confirmation_only"}),
                    "not_tradable_count": sum(1 for row in rows if row["tradability_label"] == "not_tradable"),
                    "capital_driven_count": sum(1 for row in rows if row["capital_state"] == "capital_driven_rebound"),
                    "platform_breakout_count": sum(1 for row in rows if row["breakout_state"] == "platform_breakout"),
                    "admission_state": admission_state,
                    "strict_supervisor_conclusion": strict_supervisor_conclusion,
                }
            )

        _write_csv(
            self.output_path,
            structure_rows,
            [
                "sample_window_id",
                "subwindow_id",
                "trade_date_start",
                "trade_date_end",
                "symbol",
                "display_name",
                "symbol_role",
                "start_trade_date",
                "end_trade_date",
                "start_close",
                "end_close",
                "end_return_pct",
                "window_high",
                "window_low",
                "pre20_high",
                "pre20_low",
                "window_high_vs_pre20_high_pct",
                "window_avg_volume",
                "pre5_avg_volume",
                "volume_ratio_vs_pre5",
                "up_day_count",
                "window_net_mf_amount",
                "position_state",
                "breakout_state",
                "breadth_state",
                "capital_state",
                "tradability_label",
                "trigger_role",
                "structure_gate_judgement",
                "final_training_admission",
                "strict_supervisor_note",
            ],
        )
        _write_csv(
            self.summary_path,
            summary_rows,
            [
                "sample_window_id",
                "representative_symbol_count",
                "tradable_now_count",
                "watch_only_count",
                "not_tradable_count",
                "capital_driven_count",
                "platform_breakout_count",
                "admission_state",
                "strict_supervisor_conclusion",
            ],
        )
        return MaterializedCommercialAerospaceWindowStructureSliceV1(
            structure_rows=structure_rows,
            summary_rows=summary_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    result = MaterializeCommercialAerospaceWindowStructureSliceV1(repo_root).materialize()
    print(
        f"materialized {len(result.structure_rows)} rows -> "
        f"{repo_root / 'data' / 'training' / 'commercial_aerospace_202511_202604_window_structure_slice_v1.csv'}"
    )


if __name__ == "__main__":
    main()
