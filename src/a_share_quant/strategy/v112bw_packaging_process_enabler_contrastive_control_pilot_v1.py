from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient


@dataclass(slots=True)
class V112BWPackagingProcessEnablerContrastiveControlPilotReport:
    summary: dict[str, Any]
    contrast_rows: list[dict[str, Any]]
    trade_rows: list[dict[str, Any]]
    control_action_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "contrast_rows": self.contrast_rows,
            "trade_rows": self.trade_rows,
            "control_action_rows": self.control_action_rows,
            "comparison_rows": self.comparison_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BWPackagingProcessEnablerContrastiveControlPilotAnalyzer:
    DEFAULT_HOLDING_DAYS = 20
    HOLDING_VETO_DAYS = 10
    TARGET_SYMBOL = "300757"
    TARGET_STAGE = "main_markup"
    TARGET_ROLE = "packaging_process_enabler"
    CONTRAST_FEATURES = [
        "core_branch_relative_strength_spread_state",
        "core_spillover_divergence_state",
        "spillover_saturation_overlay_state",
        "ai_hardware_cross_board_resonance_state",
    ]

    def analyze(
        self,
        *,
        bp_fusion_payload: dict[str, Any],
        bt_extraction_payload: dict[str, Any],
        bv_control_pilot_payload: dict[str, Any],
        neutral_pilot_payload: dict[str, Any],
    ) -> V112BWPackagingProcessEnablerContrastiveControlPilotReport:
        base_trade_rows = sorted(list(bp_fusion_payload.get("trade_rows", [])), key=lambda row: str(row.get("entry_date")))
        gate_rows = list(bp_fusion_payload.get("gate_decision_rows", []))
        if not base_trade_rows or not gate_rows:
            raise ValueError("V1.12BW requires the frozen fusion trade rows and gate decision rows.")

        trade_map = {(str(row.get("entry_date")), str(row.get("symbol"))): row for row in base_trade_rows}
        target_gate_rows = [
            row
            for row in gate_rows
            if str(row.get("symbol")) == self.TARGET_SYMBOL
            and (str(row.get("trade_date")), str(row.get("symbol"))) in trade_map
        ]
        if len(target_gate_rows) < 2:
            raise ValueError("V1.12BW requires at least two target gate rows for contrastive refinement.")

        contrast_rows = []
        for row in target_gate_rows:
            trade = trade_map[(str(row.get("trade_date")), str(row.get("symbol")))]
            enriched = {
                "entry_date": str(row.get("trade_date")),
                "symbol": self.TARGET_SYMBOL,
                "stage_family": str(trade.get("stage_family")),
                "role_family": str(trade.get("role_family")),
                "realized_forward_return_20d": float(trade.get("realized_forward_return_20d", 0.0)),
                "path_max_drawdown": float(trade.get("path_max_drawdown", 0.0)),
                "contrast_label": "bad_trade" if float(trade.get("realized_forward_return_20d", 0.0)) < 0.0 else "good_trade",
            }
            for feature in self.CONTRAST_FEATURES:
                enriched[feature] = float(row.get(feature, 0.0))
            contrast_rows.append(enriched)

        holding_veto_pairs = {
            (str(row.get("stage_family")), str(row.get("role_family")))
            for row in list(bt_extraction_payload.get("holding_veto_rows", []))
        }
        contributor_pair = (
            str(bv_control_pilot_payload.get("summary", {}).get("worst_trade_stage_family")),
            str(bv_control_pilot_payload.get("summary", {}).get("worst_trade_role_family")),
        )

        gate_feature_map = {(str(row.get("trade_date")), str(row.get("symbol"))): row for row in gate_rows}
        symbols = sorted({str(row.get("symbol")) for row in base_trade_rows})
        bar_cache = self._bar_cache(symbols=symbols)

        current_equity = 1.0
        trade_rows: list[dict[str, Any]] = []
        control_action_rows: list[dict[str, Any]] = []

        for trade in base_trade_rows:
            entry_date = str(trade.get("entry_date"))
            stage_family = str(trade.get("stage_family"))
            role_family = str(trade.get("role_family"))
            symbol = str(trade.get("symbol"))
            gate_row = gate_feature_map.get((entry_date, symbol), {})

            if (stage_family, role_family) == contributor_pair and self._is_contrastive_entry_veto(gate_row):
                control_action_rows.append(
                    {
                        "entry_date": entry_date,
                        "symbol": symbol,
                        "stage_family": stage_family,
                        "role_family": role_family,
                        "control_action": "contrastive_entry_veto",
                    }
                )
                continue

            holding_days = self.HOLDING_VETO_DAYS if (stage_family, role_family) in holding_veto_pairs else self.DEFAULT_HOLDING_DAYS
            if holding_days != self.DEFAULT_HOLDING_DAYS:
                control_action_rows.append(
                    {
                        "entry_date": entry_date,
                        "symbol": symbol,
                        "stage_family": stage_family,
                        "role_family": role_family,
                        "control_action": "holding_veto_half_life",
                    }
                )

            trade_path = self._trade_path(symbol=symbol, entry_date=entry_date, bars=bar_cache[symbol], holding_days=holding_days)
            if not trade_path:
                continue

            entry_equity = current_equity
            peak_equity = entry_equity
            max_path_drawdown = 0.0
            for point in trade_path:
                path_equity = entry_equity * float(point["price_ratio"])
                peak_equity = max(peak_equity, path_equity)
                if peak_equity > 0.0:
                    max_path_drawdown = min(max_path_drawdown, path_equity / peak_equity - 1.0)
            current_equity = entry_equity * float(trade_path[-1]["price_ratio"])

            trade_rows.append(
                {
                    "entry_date": entry_date,
                    "exit_date": str(trade_path[-1]["trade_date"]),
                    "symbol": symbol,
                    "stage_family": stage_family,
                    "role_family": role_family,
                    "holding_days": holding_days,
                    "ranker_score": trade.get("ranker_score"),
                    "realized_forward_return": round(current_equity / entry_equity - 1.0, 4),
                    "path_max_drawdown": round(float(max_path_drawdown), 4),
                    "entry_equity": round(entry_equity, 4),
                    "exit_equity": round(current_equity, 4),
                }
            )

        total_return = current_equity - 1.0
        max_drawdown = min((float(row["path_max_drawdown"]) for row in trade_rows), default=0.0)
        positive_sum = sum(float(row["realized_forward_return"]) for row in trade_rows if float(row["realized_forward_return"]) > 0.0)
        negative_sum = sum(float(row["realized_forward_return"]) for row in trade_rows if float(row["realized_forward_return"]) < 0.0)
        profit_factor = positive_sum / abs(negative_sum) if negative_sum < 0.0 else math.inf

        bp_summary = dict(bp_fusion_payload.get("summary", {}))
        bv_summary = dict(bv_control_pilot_payload.get("summary", {}))
        neutral_summary = dict(neutral_pilot_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "freeze_v112bw_packaging_process_enabler_contrastive_control_pilot_v1",
            "trade_count": len(trade_rows),
            "contrastive_veto_count": sum(1 for row in control_action_rows if str(row.get("control_action")) == "contrastive_entry_veto"),
            "holding_veto_half_life_count": sum(1 for row in control_action_rows if str(row.get("control_action")) == "holding_veto_half_life"),
            "total_return": round(total_return, 4),
            "max_drawdown": round(float(max_drawdown), 4),
            "profit_factor": round(float(profit_factor), 4) if profit_factor != math.inf else "inf",
            "bp_return_delta": round(total_return - float(bp_summary.get("total_return", 0.0)), 4),
            "bp_drawdown_delta": round(float(max_drawdown) - float(bp_summary.get("max_drawdown", 0.0)), 4),
            "bv_return_delta": round(total_return - float(bv_summary.get("total_return", 0.0)), 4),
            "bv_drawdown_delta": round(float(max_drawdown) - float(bv_summary.get("max_drawdown", 0.0)), 4),
            "neutral_return_delta": round(total_return - float(neutral_summary.get("total_return", 0.0)), 4),
            "neutral_drawdown_delta": round(float(max_drawdown) - float(neutral_summary.get("max_drawdown", 0.0)), 4),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_followup_next": True,
            "recommended_next_posture": "promote_contrastive_control_as_candidate_control"
            if total_return > float(bv_summary.get("total_return", 0.0)) and float(max_drawdown) >= float(bv_summary.get("max_drawdown", 0.0))
            else "keep_contrastive_control_as_candidate_only",
        }
        comparison_rows = [
            {"comparison_name": "return_vs_bp_fusion", "baseline_value": bp_summary.get("total_return"), "pilot_value": round(total_return, 4), "delta": summary["bp_return_delta"]},
            {"comparison_name": "max_drawdown_vs_bp_fusion", "baseline_value": bp_summary.get("max_drawdown"), "pilot_value": round(float(max_drawdown), 4), "delta": summary["bp_drawdown_delta"]},
            {"comparison_name": "return_vs_bv", "baseline_value": bv_summary.get("total_return"), "pilot_value": round(total_return, 4), "delta": summary["bv_return_delta"]},
            {"comparison_name": "max_drawdown_vs_bv", "baseline_value": bv_summary.get("max_drawdown"), "pilot_value": round(float(max_drawdown), 4), "delta": summary["bv_drawdown_delta"]},
            {"comparison_name": "return_vs_neutral", "baseline_value": neutral_summary.get("total_return"), "pilot_value": round(total_return, 4), "delta": summary["neutral_return_delta"]},
            {"comparison_name": "max_drawdown_vs_neutral", "baseline_value": neutral_summary.get("max_drawdown"), "pilot_value": round(float(max_drawdown), 4), "delta": summary["neutral_drawdown_delta"]},
        ]
        interpretation = [
            "V1.12BW replaces blanket contributor veto with a contrastive state-direction veto for packaging_process_enabler states.",
            "The goal is to block the bad 300757 window while preserving the later good 300757 window.",
        ]
        return V112BWPackagingProcessEnablerContrastiveControlPilotReport(
            summary=summary,
            contrast_rows=contrast_rows,
            trade_rows=trade_rows,
            control_action_rows=control_action_rows,
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )

    def _is_contrastive_entry_veto(self, gate_row: dict[str, Any]) -> bool:
        return (
            float(gate_row.get("core_branch_relative_strength_spread_state", 0.0)) < 0.0
            and float(gate_row.get("core_spillover_divergence_state", 0.0)) < 0.0
            and float(gate_row.get("spillover_saturation_overlay_state", 0.0)) > 0.0
            and float(gate_row.get("ai_hardware_cross_board_resonance_state", 0.0)) < 0.0
        )

    def _bar_cache(self, *, symbols: list[str]) -> dict[str, Any]:
        client = TencentKlineClient()
        cache = {}
        for symbol in symbols:
            frame = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
            frame["trade_date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
            cache[symbol] = frame
        return cache

    def _trade_path(self, *, symbol: str, entry_date: str, bars: Any, holding_days: int) -> list[dict[str, Any]]:
        matching = bars.index[bars["trade_date"] == entry_date].tolist()
        if not matching:
            return []
        start_idx = int(matching[0])
        end_idx = start_idx + holding_days
        if end_idx >= len(bars):
            return []
        entry_close = float(bars.iloc[start_idx]["close"])
        if entry_close == 0.0:
            return []
        rows = []
        for idx in range(start_idx, end_idx + 1):
            close = float(bars.iloc[idx]["close"])
            rows.append({"trade_date": str(bars.iloc[idx]["trade_date"]), "price_ratio": close / entry_close})
        return rows


def write_v112bw_packaging_process_enabler_contrastive_control_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BWPackagingProcessEnablerContrastiveControlPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
