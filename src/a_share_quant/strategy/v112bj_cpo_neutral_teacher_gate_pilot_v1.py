from __future__ import annotations

import json
import math
import os
from bisect import bisect_right
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient
from a_share_quant.strategy.v112am_cpo_extremely_small_core_skeleton_training_pilot_v1 import (
    V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer,
)
from a_share_quant.strategy.v112ao_cpo_role_layer_patch_pilot_v1 import (
    V112AOCPORoleLayerPatchPilotAnalyzer,
)
from a_share_quant.strategy.v112au_cpo_bounded_row_geometry_widen_pilot_v1 import (
    V112AUCPOBoundedRowGeometryWidenPilotAnalyzer,
)
from a_share_quant.strategy.v112av_cpo_branch_role_geometry_patch_pilot_v1 import (
    V112AVCPOBranchRoleGeometryPatchPilotAnalyzer,
)


@dataclass(slots=True)
class V112BJCpoNeutralTeacherGatePilotReport:
    summary: dict[str, Any]
    trade_rows: list[dict[str, Any]]
    equity_curve_rows: list[dict[str, Any]]
    drawdown_curve_rows: list[dict[str, Any]]
    teacher_decision_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    plot_bundle_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "trade_rows": self.trade_rows,
            "equity_curve_rows": self.equity_curve_rows,
            "drawdown_curve_rows": self.drawdown_curve_rows,
            "teacher_decision_rows": self.teacher_decision_rows,
            "comparison_rows": self.comparison_rows,
            "plot_bundle_rows": self.plot_bundle_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BJCpoNeutralTeacherGatePilotAnalyzer:
    HOLDING_DAYS = 20
    MIN_TRAIN_SAMPLES = 120
    MIN_GATE_SAMPLES = 80
    MIN_GATE_POSITIVES = 3

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        oracle_benchmark_payload: dict[str, Any],
        aggressive_pilot_payload: dict[str, Any],
        neutral_pilot_payload: dict[str, Any],
        ranker_pilot_payload: dict[str, Any],
        training_layer_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112BJCpoNeutralTeacherGatePilotReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112bj_now")):
            raise ValueError("V1.12BJ must be open before the neutral teacher-gate pilot runs.")

        oracle_summary = dict(oracle_benchmark_payload.get("summary", {}))
        aggressive_summary = dict(aggressive_pilot_payload.get("summary", {}))
        neutral_summary = dict(neutral_pilot_payload.get("summary", {}))
        ranker_summary = dict(ranker_pilot_payload.get("summary", {}))
        training_layer_rows = list(training_layer_payload.get("training_layer_rows", []))
        if len(training_layer_rows) != 10:
            raise ValueError("V1.12BJ expects the frozen 10-row training-facing layer.")

        pilot_analyzer = V112AMCPOExtremelySmallCoreSkeletonTrainingPilotAnalyzer()
        widen_analyzer = V112AUCPOBoundedRowGeometryWidenPilotAnalyzer()
        role_patch = V112AOCPORoleLayerPatchPilotAnalyzer()
        branch_patch = V112AVCPOBranchRoleGeometryPatchPilotAnalyzer()
        stage_map = pilot_analyzer._stage_map(list(cycle_reconstruction_payload.get("reconstructed_stage_rows", [])))  # noqa: SLF001
        samples = widen_analyzer._build_samples(  # noqa: SLF001
            widened_rows=training_layer_rows,
            stage_map=stage_map,
            pilot_analyzer=pilot_analyzer,
        )
        samples.sort(key=lambda item: item.trade_date)
        truth_index = {str(row.get("symbol")): row for row in training_layer_rows}
        impl_features = widen_analyzer._implementation_feature_map(samples=samples, truth_index=truth_index)  # noqa: SLF001
        feature_names = (
            list(pilot_analyzer.FEATURE_NAMES)
            + list(role_patch.PATCH_FEATURE_NAMES)
            + list(widen_analyzer.IMPLEMENTATION_FEATURE_NAMES)
            + list(branch_patch.BRANCH_PATCH_FEATURE_NAMES)
        )

        sample_rows: list[dict[str, Any]] = []
        for sample in samples:
            row = {
                "trade_date": sample.trade_date,
                "symbol": sample.symbol,
                "stage_family": sample.stage_family,
                "role_family": sample.role_family,
                "catalyst_sequence_label": sample.catalyst_sequence_label,
                "forward_return_20d": float(sample.forward_return_20d),
                "max_drawdown_20d": float(sample.max_drawdown_20d),
            }
            for name in pilot_analyzer.FEATURE_NAMES:
                row[name] = float(sample.feature_values[name])
            for name in role_patch.PATCH_FEATURE_NAMES:
                row[name] = float(sample.feature_values[name])
            for name in widen_analyzer.IMPLEMENTATION_FEATURE_NAMES:
                row[name] = float(impl_features[(sample.trade_date, sample.symbol)][name])
            branch_values = branch_patch._branch_patch_values(sample=sample)  # noqa: SLF001
            for idx, name in enumerate(branch_patch.BRANCH_PATCH_FEATURE_NAMES):
                row[name] = float(branch_values[idx])
            sample_rows.append(row)

        frame = pd.DataFrame(sample_rows).sort_values(["trade_date", "symbol"]).reset_index(drop=True)
        frame["winner_label"] = 0
        for _, group in frame.groupby("trade_date"):
            positive = group[group["forward_return_20d"] > 0.0]
            if positive.empty:
                continue
            winner_idx = int(positive["forward_return_20d"].idxmax())
            frame.loc[winner_idx, "winner_label"] = 1

        teacher_trade_rows = list(neutral_pilot_payload.get("trade_rows", []))
        teacher_entry_dates = {str(row.get("entry_date")) for row in teacher_trade_rows}
        teacher_cash_dates = {
            str(row.get("trade_date"))
            for row in list(neutral_pilot_payload.get("equity_curve_rows", []))
            if str(row.get("position_state")) == "cash"
        }
        ordered_dates = sorted(frame["trade_date"].unique().tolist())
        teacher_decision_rows = self._build_teacher_decision_rows(
            frame=frame,
            ordered_dates=ordered_dates,
            teacher_entry_dates=teacher_entry_dates,
            teacher_cash_dates=teacher_cash_dates,
            feature_names=feature_names,
        )
        decision_frame = pd.DataFrame(teacher_decision_rows).sort_values("trade_date").reset_index(drop=True)
        decision_dates = set(decision_frame["trade_date"].tolist())
        bar_cache = self._bar_cache(symbols=sorted(frame["symbol"].unique().tolist()))
        equity_curve_rows: list[dict[str, Any]] = []
        trade_rows: list[dict[str, Any]] = []
        current_equity = 1.0
        idx = 0
        gate_feature_names = self._gate_feature_names()

        while idx < len(ordered_dates):
            trade_date = ordered_dates[idx]
            decision_idx = idx - self.HOLDING_DAYS
            if decision_idx < 0 or trade_date not in decision_dates:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue
            cutoff_date = ordered_dates[decision_idx]
            train_gate_frame = decision_frame[decision_frame["trade_date"] <= cutoff_date].copy()
            positive_count = int(train_gate_frame["teacher_enter_label"].sum()) if not train_gate_frame.empty else 0
            if len(train_gate_frame) < self.MIN_GATE_SAMPLES or positive_count < self.MIN_GATE_POSITIVES:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue
            y_gate_train = train_gate_frame["teacher_enter_label"].to_numpy(dtype=int)
            if len(set(int(v) for v in y_gate_train)) < 2:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue
            x_gate_train = train_gate_frame[gate_feature_names].to_numpy(dtype=float)
            gate_model = HistGradientBoostingClassifier(max_depth=3, learning_rate=0.05, max_iter=120, random_state=42)
            pos_weight = len(y_gate_train) / max(positive_count, 1)
            sample_weight = np.where(y_gate_train == 1, pos_weight, 1.0)
            gate_model.fit(x_gate_train, y_gate_train, sample_weight=sample_weight)
            gate_base_rate = float(np.mean(y_gate_train))
            gate_threshold = max(0.35, gate_base_rate * 2.5)
            current_row = decision_frame[decision_frame["trade_date"] == trade_date].iloc[0]
            gate_prob = float(gate_model.predict_proba(current_row[gate_feature_names].to_frame().T.to_numpy(dtype=float))[0, 1])
            if gate_prob <= gate_threshold:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue

            chosen_symbol = str(current_row["symbol"])
            trade_path = self._trade_path(symbol=chosen_symbol, entry_date=trade_date, bars=bar_cache[chosen_symbol])
            if not trade_path:
                self._append_equity_point(equity_curve_rows, trade_date, current_equity, "cash", "CASH")
                idx += 1
                continue
            entry_equity = current_equity
            path_peak = entry_equity
            max_path_drawdown = 0.0
            for row in trade_path:
                path_equity = entry_equity * float(row["price_ratio"])
                path_peak = max(path_peak, path_equity)
                if path_peak > 0.0:
                    max_path_drawdown = min(max_path_drawdown, path_equity / path_peak - 1.0)
                self._append_equity_point(equity_curve_rows, str(row["trade_date"]), path_equity, "long", chosen_symbol)
            current_equity = float(equity_curve_rows[-1]["equity"])
            exit_date = str(trade_path[-1]["trade_date"])
            trade_rows.append(
                {
                    "entry_date": trade_date,
                    "exit_date": exit_date,
                    "symbol": chosen_symbol,
                    "stage_family": str(current_row["stage_family"]),
                    "role_family": str(current_row["role_family"]),
                    "catalyst_sequence_label": str(current_row["catalyst_sequence_label"]),
                    "teacher_enter_label": int(current_row["teacher_enter_label"]),
                    "teacher_gate_prob": round(gate_prob, 4),
                    "gate_threshold": round(float(gate_threshold), 4),
                    "teacher_selective_score": round(float(current_row["selective_score"]), 4),
                    "realized_forward_return_20d": round(current_equity / entry_equity - 1.0, 4),
                    "sample_forward_return_20d": round(float(current_row["forward_return_20d"]), 4),
                    "path_max_drawdown": round(float(max_path_drawdown), 4),
                    "entry_equity": round(entry_equity, 4),
                    "exit_equity": round(current_equity, 4),
                }
            )
            idx = self._next_index_after_exit(ordered_dates=ordered_dates, exit_date=exit_date)

        drawdown_curve_rows = self._drawdown_curve(equity_curve_rows)
        total_return = float(equity_curve_rows[-1]["equity"]) - 1.0 if equity_curve_rows else 0.0
        max_drawdown = min((float(row["drawdown"]) for row in drawdown_curve_rows), default=0.0)
        positive_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0)
        negative_sum = sum(float(row["realized_forward_return_20d"]) for row in trade_rows if float(row["realized_forward_return_20d"]) < 0.0)
        profit_factor = positive_sum / abs(negative_sum) if negative_sum < 0.0 else math.inf
        hit_rate = sum(1 for row in trade_rows if float(row["realized_forward_return_20d"]) > 0.0) / len(trade_rows) if trade_rows else 0.0
        cash_days = sum(1 for row in equity_curve_rows if str(row["position_state"]) == "cash")
        trade_entry_dates = {str(row["entry_date"]) for row in trade_rows}
        teacher_alignment_recall = len(trade_entry_dates & teacher_entry_dates) / len(teacher_entry_dates) if teacher_entry_dates else 0.0
        teacher_alignment_precision = len(trade_entry_dates & teacher_entry_dates) / len(trade_entry_dates) if trade_entry_dates else 0.0

        comparison_rows = [
            {
                "comparison_name": "return_vs_neutral",
                "neutral_value": neutral_summary.get("total_return"),
                "teacher_gate_value": round(total_return, 4),
                "delta": round(total_return - float(neutral_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "return_vs_aggressive",
                "aggressive_value": aggressive_summary.get("total_return"),
                "teacher_gate_value": round(total_return, 4),
                "delta": round(total_return - float(aggressive_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "return_vs_ranker",
                "ranker_value": ranker_summary.get("total_return"),
                "teacher_gate_value": round(total_return, 4),
                "delta": round(total_return - float(ranker_summary.get("total_return", 0.0)), 4),
            },
            {
                "comparison_name": "return_gap_vs_oracle",
                "oracle_value": oracle_summary.get("total_return"),
                "teacher_gate_value": round(total_return, 4),
                "gap": round(float(oracle_summary.get("total_return", 0.0)) - total_return, 4),
            },
        ]

        summary = {
            "acceptance_posture": "freeze_v112bj_cpo_neutral_teacher_gate_pilot_v1",
            "track_name": "neutral_teacher_gate_track",
            "no_leak_enforced": True,
            "training_layer_row_count": len(training_layer_rows),
            "sample_count": len(frame),
            "teacher_decision_row_count": len(decision_frame),
            "trade_count": len(trade_rows),
            "equity_curve_point_count": len(equity_curve_rows),
            "drawdown_curve_point_count": len(drawdown_curve_rows),
            "total_return": round(total_return, 4),
            "max_drawdown": round(float(max_drawdown), 4),
            "profit_factor": round(float(profit_factor), 4) if profit_factor != math.inf else "inf",
            "hit_rate": round(float(hit_rate), 4),
            "cash_ratio": round(float(cash_days / len(equity_curve_rows)), 4) if equity_curve_rows else 0.0,
            "teacher_alignment_recall": round(float(teacher_alignment_recall), 4),
            "teacher_alignment_precision": round(float(teacher_alignment_precision), 4),
            "neutral_return_delta": round(total_return - float(neutral_summary.get("total_return", 0.0)), 4),
            "aggressive_return_delta": round(total_return - float(aggressive_summary.get("total_return", 0.0)), 4),
            "ranker_return_delta": round(total_return - float(ranker_summary.get("total_return", 0.0)), 4),
            "oracle_return_gap": round(float(oracle_summary.get("total_return", 0.0)) - total_return, 4),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "compare_teacher_gate_vs_neutral_and_only_keep_this_line_if_it_adds_real_participation_learning_value",
        }
        interpretation = [
            "This line does not invent a new portfolio rule stack; it tries to learn the participation discipline of the current neutral teacher.",
            "Its value is highest if it can preserve low-frequency, high-quality participation without manually replaying the teacher gates.",
            "It remains bounded, no-leak, non-deployable, and report-only.",
        ]
        return V112BJCpoNeutralTeacherGatePilotReport(
            summary=summary,
            trade_rows=trade_rows,
            equity_curve_rows=equity_curve_rows,
            drawdown_curve_rows=drawdown_curve_rows,
            teacher_decision_rows=teacher_decision_rows,
            comparison_rows=comparison_rows,
            plot_bundle_rows=[
                {"plot_name": "neutral_teacher_gate_equity_curve", "series_name": "equity", "point_count": len(equity_curve_rows)},
                {"plot_name": "neutral_teacher_gate_drawdown_curve", "series_name": "drawdown", "point_count": len(drawdown_curve_rows)},
            ],
            interpretation=interpretation,
        )

    def _build_teacher_decision_rows(
        self,
        *,
        frame: pd.DataFrame,
        ordered_dates: list[str],
        teacher_entry_dates: set[str],
        teacher_cash_dates: set[str],
        feature_names: list[str],
    ) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for idx, trade_date in enumerate(ordered_dates):
            decision_idx = idx - self.HOLDING_DAYS
            if decision_idx < 0 or trade_date not in teacher_cash_dates:
                continue
            cutoff_date = ordered_dates[decision_idx]
            train_frame = frame[frame["trade_date"] <= cutoff_date]
            if len(train_frame) < self.MIN_TRAIN_SAMPLES:
                continue
            y_train = train_frame["winner_label"].to_numpy(dtype=int)
            if len(set(int(v) for v in y_train)) < 2:
                continue
            model = HistGradientBoostingClassifier(max_depth=4, learning_rate=0.05, max_iter=150, random_state=42)
            x_train = train_frame[feature_names].to_numpy(dtype=float)
            model.fit(x_train, y_train)
            base_rate = float(np.mean(y_train))
            current_frame = frame[frame["trade_date"] == trade_date].copy()
            x_current = current_frame[feature_names].to_numpy(dtype=float)
            winner_probs = model.predict_proba(x_current)[:, 1]
            current_frame["winner_prob"] = winner_probs
            current_frame["probability_margin"] = current_frame["winner_prob"] - base_rate
            current_frame["selective_score"] = (
                current_frame["probability_margin"]
                + 0.08 * current_frame["catalyst_presence_proxy"]
                + 0.06 * current_frame["weighted_breadth_ratio"]
                + 0.04 * current_frame["confidence_tier_numeric"]
                + 0.03 * current_frame["rollforward_state_numeric"].clip(lower=0.0)
                - 0.05 * current_frame["turnover_state_numeric"]
                - 0.03 * current_frame["window_uncertainty_numeric"]
                - 0.02 * current_frame["realized_vol_10"]
                - 0.02 * current_frame["volume_cv_10"]
            )
            chosen_row = current_frame.sort_values(
                ["selective_score", "winner_prob", "forward_return_20d"],
                ascending=[False, False, False],
            ).iloc[0]
            rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": str(chosen_row["symbol"]),
                    "stage_family": str(chosen_row["stage_family"]),
                    "role_family": str(chosen_row["role_family"]),
                    "catalyst_sequence_label": str(chosen_row["catalyst_sequence_label"]),
                    "teacher_enter_label": 1 if trade_date in teacher_entry_dates else 0,
                    "winner_prob": float(chosen_row["winner_prob"]),
                    "probability_margin": float(chosen_row["probability_margin"]),
                    "selective_score": float(chosen_row["selective_score"]),
                    "weighted_breadth_ratio": float(chosen_row["weighted_breadth_ratio"]),
                    "catalyst_presence_proxy": float(chosen_row["catalyst_presence_proxy"]),
                    "confidence_tier_numeric": float(chosen_row["confidence_tier_numeric"]),
                    "rollforward_state_numeric": float(chosen_row["rollforward_state_numeric"]),
                    "turnover_state_numeric": float(chosen_row["turnover_state_numeric"]),
                    "window_uncertainty_numeric": float(chosen_row["window_uncertainty_numeric"]),
                    "realized_vol_10": float(chosen_row["realized_vol_10"]),
                    "volume_cv_10": float(chosen_row["volume_cv_10"]),
                    "forward_return_20d": float(chosen_row["forward_return_20d"]),
                }
            )
        return rows

    def _gate_feature_names(self) -> list[str]:
        return [
            "winner_prob",
            "probability_margin",
            "selective_score",
            "weighted_breadth_ratio",
            "catalyst_presence_proxy",
            "confidence_tier_numeric",
            "rollforward_state_numeric",
            "turnover_state_numeric",
            "window_uncertainty_numeric",
            "realized_vol_10",
            "volume_cv_10",
        ]

    def _bar_cache(self, *, symbols: list[str]) -> dict[str, pd.DataFrame]:
        client = TencentKlineClient()
        cache: dict[str, pd.DataFrame] = {}
        for symbol in symbols:
            frame = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
            frame["trade_date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
            cache[symbol] = frame
        return cache

    def _trade_path(self, *, symbol: str, entry_date: str, bars: pd.DataFrame) -> list[dict[str, Any]]:
        matching = bars.index[bars["trade_date"] == entry_date].tolist()
        if not matching:
            return []
        start_idx = int(matching[0])
        end_idx = start_idx + self.HOLDING_DAYS
        if end_idx >= len(bars):
            return []
        entry_close = float(bars.iloc[start_idx]["close"])
        if entry_close == 0.0:
            return []
        rows: list[dict[str, Any]] = []
        for idx in range(start_idx, end_idx + 1):
            close = float(bars.iloc[idx]["close"])
            rows.append({"trade_date": str(bars.iloc[idx]["trade_date"]), "price_ratio": close / entry_close})
        return rows

    def _append_equity_point(
        self,
        equity_curve_rows: list[dict[str, Any]],
        trade_date: str,
        equity: float,
        position_state: str,
        symbol: str,
    ) -> None:
        row = {
            "trade_date": trade_date,
            "equity": round(float(equity), 6),
            "position_state": position_state,
            "symbol": symbol,
        }
        if equity_curve_rows and str(equity_curve_rows[-1]["trade_date"]) == trade_date:
            equity_curve_rows[-1] = row
        else:
            equity_curve_rows.append(row)

    def _drawdown_curve(self, equity_curve_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        peak = 0.0
        rows: list[dict[str, Any]] = []
        for row in equity_curve_rows:
            equity = float(row["equity"])
            peak = max(peak, equity)
            drawdown = equity / peak - 1.0 if peak > 0.0 else 0.0
            rows.append({"trade_date": str(row["trade_date"]), "drawdown": round(float(drawdown), 6)})
        return rows

    def _next_index_after_exit(self, *, ordered_dates: list[str], exit_date: str) -> int:
        return bisect_right(ordered_dates, exit_date)


def write_v112bj_cpo_neutral_teacher_gate_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BJCpoNeutralTeacherGatePilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
