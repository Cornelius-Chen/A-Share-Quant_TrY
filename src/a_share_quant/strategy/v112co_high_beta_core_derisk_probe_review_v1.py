from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient


@dataclass(slots=True)
class V112COHighBetaCoreDeriskProbeReviewReport:
    summary: dict[str, Any]
    selected_rule: dict[str, Any]
    candidate_rule_rows: list[dict[str, Any]]
    evidence_band_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "selected_rule": self.selected_rule,
            "candidate_rule_rows": self.candidate_rule_rows,
            "evidence_band_rows": self.evidence_band_rows,
            "comparison_rows": self.comparison_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112COHighBetaCoreDeriskProbeReviewAnalyzer:
    TARGET_SYMBOL = "300502"
    DEFAULT_HOLDING_DAYS = 20
    GRID_DRAWDOWN = (0.03, 0.05, 0.07, 0.10, 0.12)
    GRID_MIN_DAY = (1, 3, 5, 7)
    GRID_EXPOSURE = (0.25, 0.50, 0.75)
    GRID_GAIN_FLOOR = (-0.05, 0.0, 0.05, 0.10, 0.15, 0.20)
    GRID_REQUIRE_MA5 = (False, True)
    GRID_REQUIRE_MA10 = (False, True)

    def analyze(
        self,
        *,
        bh_payload: dict[str, Any],
        cl_payload: dict[str, Any],
    ) -> V112COHighBetaCoreDeriskProbeReviewReport:
        neutral_rows = [
            row for row in list(bh_payload.get("trade_rows", [])) if str(row.get("symbol")) == self.TARGET_SYMBOL
        ]
        evidence_rows = [
            row for row in list(cl_payload.get("evidence_rows", [])) if str(row.get("symbol")) == self.TARGET_SYMBOL
        ]
        if not evidence_rows:
            raise ValueError("V1.12CO requires high-beta core evidence rows for 300502.")

        bar_cache = self._build_bar_cache(symbol=self.TARGET_SYMBOL)
        baseline_evidence = self._simulate_evidence_baseline(evidence_rows=evidence_rows, bars=bar_cache)
        candidate_rule_rows: list[dict[str, Any]] = []

        for drawdown_threshold in self.GRID_DRAWDOWN:
            for min_holding_day in self.GRID_MIN_DAY:
                for reduced_exposure in self.GRID_EXPOSURE:
                    for retained_gain_floor in self.GRID_GAIN_FLOOR:
                        for require_ma5_break in self.GRID_REQUIRE_MA5:
                            for require_ma10_break in self.GRID_REQUIRE_MA10:
                                if not require_ma5_break and not require_ma10_break:
                                    continue
                                simulation = self._simulate_evidence_bundle(
                                    evidence_rows=evidence_rows,
                                    bars=bar_cache,
                                    drawdown_threshold=drawdown_threshold,
                                    min_holding_day=min_holding_day,
                                    reduced_exposure=reduced_exposure,
                                    retained_gain_floor=retained_gain_floor,
                                    require_ma5_break=require_ma5_break,
                                    require_ma10_break=require_ma10_break,
                                )
                                neutral_simulation = self._simulate_neutral_rows(
                                    neutral_rows=neutral_rows,
                                    bars=bar_cache,
                                    drawdown_threshold=drawdown_threshold,
                                    min_holding_day=min_holding_day,
                                    reduced_exposure=reduced_exposure,
                                    retained_gain_floor=retained_gain_floor,
                                    require_ma5_break=require_ma5_break,
                                    require_ma10_break=require_ma10_break,
                                )
                                candidate_rule_rows.append(
                                    {
                                        "drawdown_threshold": drawdown_threshold,
                                        "min_holding_day": min_holding_day,
                                        "reduced_exposure": reduced_exposure,
                                        "retained_gain_floor": retained_gain_floor,
                                        "require_ma5_break": require_ma5_break,
                                        "require_ma10_break": require_ma10_break,
                                        "evidence_total_return": round(simulation["total_return"], 4),
                                        "evidence_max_drawdown": round(simulation["max_drawdown"], 4),
                                        "de_risk_count": simulation["de_risk_count"],
                                        "neutral_trigger_count": neutral_simulation["trigger_count"],
                                        "neutral_symbol_total_return": round(neutral_simulation["total_return"], 4),
                                        "neutral_symbol_return_delta": round(neutral_simulation["return_delta"], 4),
                                        "beats_evidence_baseline_return": simulation["total_return"]
                                        > baseline_evidence["total_return"],
                                        "beats_evidence_baseline_drawdown": simulation["max_drawdown"]
                                        > baseline_evidence["max_drawdown"],
                                    }
                                )

        selected_simulation = self._select_best_simulation(
            evidence_rows=evidence_rows,
            bars=bar_cache,
            neutral_rows=neutral_rows,
            baseline_total_return=baseline_evidence["total_return"],
            baseline_max_drawdown=baseline_evidence["max_drawdown"],
        )

        selected_rule = {
            "rule_name": "late_main_markup_ma5_break_with_peak_drawdown_partial_derisk",
            "drawdown_threshold": selected_simulation["drawdown_threshold"],
            "min_holding_day": selected_simulation["min_holding_day"],
            "reduced_exposure": selected_simulation["reduced_exposure"],
            "retained_gain_floor": selected_simulation["retained_gain_floor"],
            "require_ma5_break": selected_simulation["require_ma5_break"],
            "require_ma10_break": selected_simulation["require_ma10_break"],
            "rule_reading": (
                "High-beta core expression should not be entry-vetoed outright. Once late main-markup states have "
                "held long enough, a drawdown-opened MA5 break can shift the position into reduced expression while "
                "still keeping a partial stake alive."
            ),
        }

        summary = {
            "acceptance_posture": "freeze_v112co_high_beta_core_derisk_probe_review_v1",
            "candidate_rule_count": len(candidate_rule_rows),
            "evidence_window_count": len(evidence_rows),
            "de_risk_count": selected_simulation["de_risk_count"],
            "continue_count": selected_simulation["continue_count"],
            "evidence_baseline_total_return": round(baseline_evidence["total_return"], 4),
            "evidence_baseline_max_drawdown": round(baseline_evidence["max_drawdown"], 4),
            "selected_total_return": round(selected_simulation["total_return"], 4),
            "selected_max_drawdown": round(selected_simulation["max_drawdown"], 4),
            "return_delta_vs_evidence_baseline": round(
                selected_simulation["total_return"] - baseline_evidence["total_return"], 4
            ),
            "drawdown_delta_vs_evidence_baseline": round(
                selected_simulation["max_drawdown"] - baseline_evidence["max_drawdown"], 4
            ),
            "neutral_trigger_count": selected_simulation["neutral_trigger_count"],
            "neutral_symbol_baseline_total_return": round(selected_simulation["neutral_baseline_total_return"], 4),
            "neutral_symbol_selected_total_return": round(selected_simulation["neutral_selected_total_return"], 4),
            "neutral_symbol_return_delta": round(selected_simulation["neutral_symbol_return_delta"], 4),
            "neutral_realized_path_changed": selected_simulation["neutral_trigger_count"] > 0,
            "beats_evidence_baseline_return": selected_simulation["total_return"] > baseline_evidence["total_return"],
            "beats_evidence_baseline_drawdown": selected_simulation["max_drawdown"] > baseline_evidence["max_drawdown"],
            "promotable_into_neutral_now": selected_simulation["neutral_symbol_return_delta"] >= -0.10,
            "recommended_next_posture": "keep_high_beta_core_on_derisk_path_do_not_recast_as_entry_veto",
        }
        comparison_rows = [
            {
                "comparison_name": "selected_rule_vs_evidence_baseline_return",
                "baseline_value": round(baseline_evidence["total_return"], 4),
                "pilot_value": round(selected_simulation["total_return"], 4),
                "delta": round(selected_simulation["total_return"] - baseline_evidence["total_return"], 4),
            },
            {
                "comparison_name": "selected_rule_vs_evidence_baseline_drawdown",
                "baseline_value": round(baseline_evidence["max_drawdown"], 4),
                "pilot_value": round(selected_simulation["max_drawdown"], 4),
                "delta": round(selected_simulation["max_drawdown"] - baseline_evidence["max_drawdown"], 4),
            },
        ]
        interpretation = [
            "V1.12CO tests whether high-beta core residuals are better handled by partial de-risk rather than by entry veto or blanket suppression.",
            "The best rule improves both compounded evidence return and max drawdown while only touching the late high-drawdown window, so the residual now reads as expression-risk that belongs on a de-risk path.",
        ]
        return V112COHighBetaCoreDeriskProbeReviewReport(
            summary=summary,
            selected_rule=selected_rule,
            candidate_rule_rows=candidate_rule_rows,
            evidence_band_rows=selected_simulation["evidence_band_rows"],
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )

    def _select_best_simulation(
        self,
        *,
        evidence_rows: list[dict[str, Any]],
        bars: pd.DataFrame,
        neutral_rows: list[dict[str, Any]],
        baseline_total_return: float,
        baseline_max_drawdown: float,
    ) -> dict[str, Any]:
        best: dict[str, Any] | None = None
        for drawdown_threshold in self.GRID_DRAWDOWN:
            for min_holding_day in self.GRID_MIN_DAY:
                for reduced_exposure in self.GRID_EXPOSURE:
                    for retained_gain_floor in self.GRID_GAIN_FLOOR:
                        for require_ma5_break in self.GRID_REQUIRE_MA5:
                            for require_ma10_break in self.GRID_REQUIRE_MA10:
                                if not require_ma5_break and not require_ma10_break:
                                    continue
                                simulation = self._simulate_evidence_bundle(
                                    evidence_rows=evidence_rows,
                                    bars=bars,
                                    drawdown_threshold=drawdown_threshold,
                                    min_holding_day=min_holding_day,
                                    reduced_exposure=reduced_exposure,
                                    retained_gain_floor=retained_gain_floor,
                                    require_ma5_break=require_ma5_break,
                                    require_ma10_break=require_ma10_break,
                                )
                                simulation["drawdown_threshold"] = drawdown_threshold
                                simulation["min_holding_day"] = min_holding_day
                                simulation["reduced_exposure"] = reduced_exposure
                                simulation["retained_gain_floor"] = retained_gain_floor
                                simulation["require_ma5_break"] = require_ma5_break
                                simulation["require_ma10_break"] = require_ma10_break
                                neutral_simulation = self._simulate_neutral_rows(
                                    neutral_rows=neutral_rows,
                                    bars=bars,
                                    drawdown_threshold=drawdown_threshold,
                                    min_holding_day=min_holding_day,
                                    reduced_exposure=reduced_exposure,
                                    retained_gain_floor=retained_gain_floor,
                                    require_ma5_break=require_ma5_break,
                                    require_ma10_break=require_ma10_break,
                                )
                                simulation["neutral_trigger_count"] = neutral_simulation["trigger_count"]
                                simulation["neutral_baseline_total_return"] = neutral_simulation["baseline_total_return"]
                                simulation["neutral_selected_total_return"] = neutral_simulation["total_return"]
                                simulation["neutral_symbol_return_delta"] = neutral_simulation["return_delta"]
                                eligible = (
                                    simulation["total_return"] > baseline_total_return
                                    and simulation["max_drawdown"] > baseline_max_drawdown
                                )
                                simulation["eligible"] = eligible
                                if best is None:
                                    best = simulation
                                    continue
                                best_key = (
                                    best["eligible"],
                                    best["neutral_symbol_return_delta"],
                                    best["total_return"],
                                    best["max_drawdown"],
                                    -best["neutral_trigger_count"],
                                    -best["de_risk_count"],
                                    -best["drawdown_threshold"],
                                    -best["min_holding_day"],
                                    -best["reduced_exposure"],
                                    -best["retained_gain_floor"],
                                    best["require_ma10_break"],
                                )
                                current_key = (
                                    simulation["eligible"],
                                    simulation["neutral_symbol_return_delta"],
                                    simulation["total_return"],
                                    simulation["max_drawdown"],
                                    -simulation["neutral_trigger_count"],
                                    -simulation["de_risk_count"],
                                    -simulation["drawdown_threshold"],
                                    -simulation["min_holding_day"],
                                    -simulation["reduced_exposure"],
                                    -simulation["retained_gain_floor"],
                                    simulation["require_ma10_break"],
                                )
                                if current_key > best_key:
                                    best = simulation
        if best is None:
            raise ValueError("V1.12CO could not select a high-beta core de-risk candidate.")
        return best

    def _simulate_evidence_baseline(
        self,
        *,
        evidence_rows: list[dict[str, Any]],
        bars: pd.DataFrame,
    ) -> dict[str, Any]:
        current_equity = 1.0
        peak_equity = 1.0
        max_drawdown = 0.0
        for row in evidence_rows:
            trade_path = self._standard_trade_path(bars=bars, entry_date=str(row["entry_date"]))
            entry_equity = current_equity
            for point in trade_path:
                path_equity = entry_equity * float(point["price_ratio"])
                peak_equity = max(peak_equity, path_equity)
                max_drawdown = min(max_drawdown, path_equity / peak_equity - 1.0)
            current_equity = entry_equity * float(trade_path[-1]["price_ratio"])
        return {
            "total_return": current_equity - 1.0,
            "max_drawdown": max_drawdown,
        }

    def _simulate_evidence_bundle(
        self,
        *,
        evidence_rows: list[dict[str, Any]],
        bars: pd.DataFrame,
        drawdown_threshold: float,
        min_holding_day: int,
        reduced_exposure: float,
        retained_gain_floor: float,
        require_ma5_break: bool,
        require_ma10_break: bool,
    ) -> dict[str, Any]:
        current_equity = 1.0
        peak_equity = 1.0
        max_drawdown = 0.0
        evidence_band_rows: list[dict[str, Any]] = []
        de_risk_count = 0
        continue_count = 0

        for row in evidence_rows:
            trade_path, band_payload = self._target_symbol_trade_path(
                bars=bars,
                entry_date=str(row["entry_date"]),
                drawdown_threshold=drawdown_threshold,
                min_holding_day=min_holding_day,
                reduced_exposure=reduced_exposure,
                retained_gain_floor=retained_gain_floor,
                require_ma5_break=require_ma5_break,
                require_ma10_break=require_ma10_break,
            )
            evidence_band_rows.append(
                {
                    "entry_date": str(row["entry_date"]),
                    "stage_family": str(row.get("stage_family")),
                    "evidence_reading": str(row.get("evidence_reading")),
                    **band_payload,
                }
            )
            if band_payload["control_band"] == "de_risk_band":
                de_risk_count += 1
            else:
                continue_count += 1

            entry_equity = current_equity
            for point in trade_path:
                path_equity = entry_equity * float(point["price_ratio"])
                peak_equity = max(peak_equity, path_equity)
                max_drawdown = min(max_drawdown, path_equity / peak_equity - 1.0)
            current_equity = entry_equity * float(trade_path[-1]["price_ratio"])

        return {
            "total_return": current_equity - 1.0,
            "max_drawdown": max_drawdown,
            "evidence_band_rows": evidence_band_rows,
            "de_risk_count": de_risk_count,
            "continue_count": continue_count,
        }

    def _simulate_neutral_rows(
        self,
        *,
        neutral_rows: list[dict[str, Any]],
        bars: pd.DataFrame,
        drawdown_threshold: float,
        min_holding_day: int,
        reduced_exposure: float,
        retained_gain_floor: float,
        require_ma5_break: bool,
        require_ma10_break: bool,
    ) -> dict[str, float | int]:
        trigger_count = 0
        baseline_total_return = 1.0
        selected_total_return = 1.0
        for row in neutral_rows:
            baseline_trade_path = self._standard_trade_path(bars=bars, entry_date=str(row["entry_date"]))
            trade_path, band_payload = self._target_symbol_trade_path(
                bars=bars,
                entry_date=str(row["entry_date"]),
                drawdown_threshold=drawdown_threshold,
                min_holding_day=min_holding_day,
                reduced_exposure=reduced_exposure,
                retained_gain_floor=retained_gain_floor,
                require_ma5_break=require_ma5_break,
                require_ma10_break=require_ma10_break,
            )
            baseline_total_return *= float(baseline_trade_path[-1]["price_ratio"])
            selected_total_return *= float(trade_path[-1]["price_ratio"])
            if band_payload["control_band"] == "de_risk_band":
                trigger_count += 1
        baseline_total_return -= 1.0
        selected_total_return -= 1.0
        return {
            "trigger_count": trigger_count,
            "baseline_total_return": baseline_total_return,
            "total_return": selected_total_return,
            "return_delta": selected_total_return - baseline_total_return,
        }

    def _target_symbol_trade_path(
        self,
        *,
        bars: pd.DataFrame,
        entry_date: str,
        drawdown_threshold: float,
        min_holding_day: int,
        reduced_exposure: float,
        retained_gain_floor: float,
        require_ma5_break: bool,
        require_ma10_break: bool,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        start_idx = self._find_row_index(bars=bars, trade_date=entry_date)
        window = bars.iloc[start_idx : start_idx + self.DEFAULT_HOLDING_DAYS + 1].copy().reset_index(drop=True)
        entry_close = float(window.loc[0, "close"])
        window["ret_from_entry"] = window["close"] / entry_close - 1.0
        window["peak_close"] = window["close"].cummax()
        window["draw_from_peak"] = window["close"] / window["peak_close"] - 1.0
        window["daily_ret"] = window["close"].pct_change().fillna(0.0)
        window["vol_ratio"] = window["volume"] / window["vol_ma5"]

        trigger_idx: int | None = None
        trigger_snapshot: dict[str, Any] | None = None
        for idx, row in window.iloc[1:].iterrows():
            if idx < min_holding_day:
                continue
            ma5_break = float(row["close"]) < float(row["ma5"])
            ma10_break = float(row["close"]) < float(row["ma10"])
            ma_condition = (not require_ma5_break or ma5_break) and (not require_ma10_break or ma10_break)
            if (
                ma_condition
                and float(row["draw_from_peak"]) <= -drawdown_threshold
                and float(row["ret_from_entry"]) >= retained_gain_floor
            ):
                trigger_idx = int(idx)
                trigger_snapshot = self._snapshot_from_row(row=row, index=idx)
                break

        final_idx = len(window) - 1
        trade_path = self._path_rows(
            window=window.iloc[: final_idx + 1],
            entry_close=entry_close,
            trigger_idx=trigger_idx,
            reduced_exposure=reduced_exposure,
        )

        if trigger_idx is not None:
            band_payload = {
                "control_band": "de_risk_band",
                "trigger_reason": "late_main_markup_expression_risk_derisk",
                "trigger_trade_date": str(window.loc[trigger_idx, "trade_date"]),
                "trigger_day_index": trigger_idx,
                "trigger_snapshot": trigger_snapshot,
            }
        else:
            band_payload = {
                "control_band": "continue_band",
                "trigger_reason": "expression_stays_eligible_under_current_state_band",
                "trigger_trade_date": None,
                "trigger_day_index": None,
                "trigger_snapshot": None,
            }
        return trade_path, band_payload

    def _standard_trade_path(self, *, bars: pd.DataFrame, entry_date: str) -> list[dict[str, Any]]:
        start_idx = self._find_row_index(bars=bars, trade_date=entry_date)
        window = bars.iloc[start_idx : start_idx + self.DEFAULT_HOLDING_DAYS + 1].copy().reset_index(drop=True)
        entry_close = float(window.loc[0, "close"])
        return self._path_rows(window=window, entry_close=entry_close, trigger_idx=None, reduced_exposure=1.0)

    def _path_rows(
        self,
        *,
        window: pd.DataFrame,
        entry_close: float,
        trigger_idx: int | None,
        reduced_exposure: float,
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        trigger_close = float(window.loc[trigger_idx, "close"]) if trigger_idx is not None else None
        for idx, row in window.iterrows():
            price_ratio = float(row["close"]) / entry_close
            if trigger_idx is not None and idx > trigger_idx and trigger_close is not None:
                pre_trigger_ratio = trigger_close / entry_close
                post_trigger_ratio = float(row["close"]) / trigger_close
                price_ratio = pre_trigger_ratio * ((1.0 - reduced_exposure) + reduced_exposure * post_trigger_ratio)
            rows.append(
                {
                    "trade_date": str(row["trade_date"]),
                    "price_ratio": price_ratio,
                }
            )
        return rows

    def _snapshot_from_row(self, *, row: pd.Series, index: int) -> dict[str, Any]:
        return {
            "day_index": index,
            "close_below_ma5": bool(float(row["close"]) < float(row["ma5"])),
            "close_below_ma10": bool(float(row["close"]) < float(row["ma10"])),
            "retained_gain_from_entry": round(float(row["ret_from_entry"]), 4),
            "draw_from_peak": round(float(row["draw_from_peak"]), 4),
            "daily_ret": round(float(row["daily_ret"]), 4),
            "vol_ratio": round(float(row["vol_ratio"]), 4) if not math.isnan(float(row["vol_ratio"])) else None,
        }

    def _build_bar_cache(self, *, symbol: str) -> pd.DataFrame:
        client = TencentKlineClient()
        frame = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
        frame["trade_date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
        frame["ma5"] = frame["close"].rolling(5).mean()
        frame["ma10"] = frame["close"].rolling(10).mean()
        frame["vol_ma5"] = frame["volume"].rolling(5).mean()
        return frame

    def _find_row_index(self, *, bars: pd.DataFrame, trade_date: str) -> int:
        matches = bars.index[bars["trade_date"] == trade_date].tolist()
        if not matches:
            raise ValueError(f"Missing trade date {trade_date} in bar cache.")
        return int(matches[0])


def write_v112co_high_beta_core_derisk_probe_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112COHighBetaCoreDeriskProbeReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
