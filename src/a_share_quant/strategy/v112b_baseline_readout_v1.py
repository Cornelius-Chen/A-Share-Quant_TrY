from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient


@dataclass(slots=True)
class TrainingSample:
    trade_date: str
    symbol: str
    stage: str
    label: str
    feature_values: dict[str, float]
    forward_return_20d: float
    max_drawdown_20d: float
    forward_return_bucket: str
    max_drawdown_bucket: str


@dataclass(slots=True)
class V112BBaselineReadoutReport:
    summary: dict[str, Any]
    feature_names: list[str]
    dataset_summary_rows: list[dict[str, Any]]
    sample_rows_preview: list[dict[str, Any]]
    fold_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_names": self.feature_names,
            "dataset_summary_rows": self.dataset_summary_rows,
            "sample_rows_preview": self.sample_rows_preview,
            "fold_rows": self.fold_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BBaselineReadoutAnalyzer:
    """Run the first report-only time-split baseline on the frozen optical-link pilot."""

    FEATURE_NAMES = [
        "product_price_change_proxy",
        "demand_acceleration_proxy",
        "supply_tightness_proxy",
        "official_or_industry_catalyst_presence",
        "revenue_sensitivity_class",
        "gross_margin_sensitivity_class",
        "order_or_capacity_sensitivity_proxy",
        "earnings_revision_pressure_proxy",
        "rerating_gap_proxy",
        "relative_strength_persistence",
        "volume_expansion_confirmation",
        "breakout_or_hold_structure",
    ]

    STATIC_ROLE_FEATURES = {
        "300308": {
            "revenue_sensitivity_class": 0.85,
            "gross_margin_sensitivity_class": 0.75,
        },
        "300502": {
            "revenue_sensitivity_class": 1.0,
            "gross_margin_sensitivity_class": 0.9,
        },
        "300394": {
            "revenue_sensitivity_class": 0.7,
            "gross_margin_sensitivity_class": 0.8,
        },
    }

    STAGE_STRENGTH = {
        "first_markup": 0.8,
        "cooling_and_box": 0.25,
        "second_markup": 0.7,
        "deep_box_reset": 0.15,
        "long_box_reset": 0.15,
        "major_markup": 1.0,
        "high_level_consolidation": 0.5,
        "pullback": 0.35,
        "rebound": 0.7,
    }

    STAGE_CATALYST_FLAG = {
        "first_markup": 1.0,
        "cooling_and_box": 0.0,
        "second_markup": 1.0,
        "deep_box_reset": 0.0,
        "long_box_reset": 0.0,
        "major_markup": 1.0,
        "high_level_consolidation": 0.5,
        "pullback": 0.0,
        "rebound": 1.0,
    }

    def analyze(
        self,
        *,
        pilot_dataset_payload: dict[str, Any],
        training_protocol_payload: dict[str, Any],
        bar_frames_by_symbol: dict[str, pd.DataFrame] | None = None,
    ) -> V112BBaselineReadoutReport:
        protocol_summary = dict(training_protocol_payload.get("summary", {}))
        if str(protocol_summary.get("acceptance_posture")) != "freeze_v112_training_protocol_v1":
            raise ValueError("V1.12 baseline readout requires the frozen V1.12 protocol.")

        rows = list(pilot_dataset_payload.get("dataset_rows", []))
        if not rows:
            raise ValueError("Pilot dataset freeze must provide rows before the baseline readout can run.")

        client = TencentKlineClient()
        sample_rows: list[TrainingSample] = []
        dataset_summary_rows: list[dict[str, Any]] = []
        for row in rows:
            symbol = str(row.get("symbol"))
            bars = (
                bar_frames_by_symbol[symbol].copy()
                if bar_frames_by_symbol and symbol in bar_frames_by_symbol
                else client.fetch_daily_bars(symbol).copy()
            )
            inferred_rows = self._build_symbol_samples(symbol=symbol, cycle_window=dict(row.get("cycle_window", {})), bars=bars)
            sample_rows.extend(inferred_rows)
            dataset_summary_rows.append(
                {
                    "symbol": symbol,
                    "name": str(row.get("name", "")),
                    "final_role_label_cn": str(row.get("final_role_label_cn", "")),
                    "sample_count": len(inferred_rows),
                    "cycle_start": min(sample.trade_date for sample in inferred_rows) if inferred_rows else None,
                    "cycle_end": max(sample.trade_date for sample in inferred_rows) if inferred_rows else None,
                    "class_distribution": self._distribution([sample.label for sample in inferred_rows]),
                }
            )

        if len(sample_rows) < 10:
            raise ValueError("The first baseline readout needs at least 10 daily samples.")

        feature_matrix = np.array(
            [[sample.feature_values[name] for name in self.FEATURE_NAMES] for sample in sample_rows],
            dtype=float,
        )
        labels = [sample.label for sample in sample_rows]
        classes = sorted(set(labels))
        label_ids = np.array([classes.index(label) for label in labels], dtype=int)
        order = np.argsort([sample.trade_date for sample in sample_rows])
        feature_matrix = feature_matrix[order]
        label_ids = label_ids[order]
        ordered_samples = [sample_rows[int(idx)] for idx in order]

        split_index = max(1, min(len(ordered_samples) - 1, int(len(ordered_samples) * 0.7)))
        x_train = feature_matrix[:split_index]
        y_train = label_ids[:split_index]
        x_test = feature_matrix[split_index:]
        y_test = label_ids[split_index:]
        ordered_test_samples = ordered_samples[split_index:]

        mean = x_train.mean(axis=0)
        std = x_train.std(axis=0)
        std[std == 0.0] = 1.0
        x_train_scaled = (x_train - mean) / std
        x_test_scaled = (x_test - mean) / std

        centroids = []
        centroid_classes = []
        for class_id in sorted(set(int(value) for value in y_train)):
            centroids.append(x_train_scaled[y_train == class_id].mean(axis=0))
            centroid_classes.append(class_id)
        centroid_matrix = np.vstack(centroids)

        fold_rows: list[dict[str, Any]] = []
        for idx, sample in enumerate(ordered_test_samples):
            distances = np.linalg.norm(centroid_matrix - x_test_scaled[idx], axis=1)
            pred_class = int(centroid_classes[int(np.argmin(distances))])
            true_class = int(y_test[idx])
            fold_rows.append(
                {
                    "trade_date": sample.trade_date,
                    "symbol": sample.symbol,
                    "stage": sample.stage,
                    "predicted_label": classes[pred_class],
                    "true_label": classes[true_class],
                    "correct": pred_class == true_class,
                }
            )

        test_accuracy = sum(1 for row in fold_rows if bool(row["correct"])) / len(fold_rows)
        summary = {
            "acceptance_posture": "freeze_v112b_first_report_only_baseline_readout_v1",
            "sample_count": len(ordered_samples),
            "train_count": int(split_index),
            "test_count": int(len(ordered_samples) - split_index),
            "class_count": len(classes),
            "class_labels": classes,
            "carry_outcome_distribution": self._distribution([sample.label for sample in ordered_samples]),
            "test_accuracy": round(float(test_accuracy), 4),
            "allow_strategy_training_now": False,
            "allow_black_box_deployment_now": False,
            "ready_for_phase_check_next": True,
        }
        sample_rows_preview = [
            {
                "trade_date": sample.trade_date,
                "symbol": sample.symbol,
                "stage": sample.stage,
                "forward_return_bucket": sample.forward_return_bucket,
                "max_drawdown_bucket": sample.max_drawdown_bucket,
                "carry_outcome_class": sample.label,
                **sample.feature_values,
            }
            for sample in ordered_samples[:12]
        ]
        interpretation = [
            "This is the first report-only baseline readout on the frozen optical-link pilot dataset.",
            "The readout uses a simple time-split nearest-centroid baseline so the first experiment stays interpretable and bounded.",
            "The result is only for owner review of the training pipeline; it does not open strategy training or model deployment.",
        ]
        return V112BBaselineReadoutReport(
            summary=summary,
            feature_names=self.FEATURE_NAMES,
            dataset_summary_rows=dataset_summary_rows,
            sample_rows_preview=sample_rows_preview,
            fold_rows=fold_rows,
            interpretation=interpretation,
        )

    def _build_symbol_samples(
        self,
        *,
        symbol: str,
        cycle_window: dict[str, str],
        bars: pd.DataFrame,
    ) -> list[TrainingSample]:
        frame = bars.copy().sort_values("date").reset_index(drop=True)
        frame["ret_5"] = frame["close"].pct_change(5)
        frame["ret_20"] = frame["close"].pct_change(20)
        frame["ma20"] = frame["close"].rolling(20, min_periods=5).mean()
        frame["ma60"] = frame["close"].rolling(60, min_periods=20).mean()
        frame["high60"] = frame["high"].rolling(60, min_periods=20).max()
        frame["high120"] = frame["high"].rolling(120, min_periods=20).max()
        frame["vol5"] = frame["volume"].rolling(5, min_periods=3).mean()
        frame["vol20"] = frame["volume"].rolling(20, min_periods=5).mean()
        frame["future_close_20"] = frame["close"].shift(-20)
        frame["future_min_low_20"] = frame["low"][::-1].rolling(20, min_periods=1).min()[::-1].shift(-1)

        cycle_start, cycle_end = self._cycle_span(cycle_window)
        within_cycle = frame["date"].dt.strftime("%Y-%m").between(cycle_start, cycle_end)
        frame = frame.loc[within_cycle].reset_index(drop=True)

        samples: list[TrainingSample] = []
        for row in frame.itertuples(index=False):
            if pd.isna(row.future_close_20) or pd.isna(row.future_min_low_20):
                continue
            stage = self._resolve_stage(cycle_window=cycle_window, trade_date=pd.Timestamp(row.date))
            if stage is None:
                continue
            forward_return = float(row.future_close_20 / row.close - 1.0)
            max_drawdown = float(row.future_min_low_20 / row.close - 1.0)
            features = self._feature_row(
                symbol=symbol,
                stage=stage,
                close=float(row.close),
                ret_5=float(row.ret_5) if pd.notna(row.ret_5) else 0.0,
                ret_20=float(row.ret_20) if pd.notna(row.ret_20) else 0.0,
                ma20=float(row.ma20) if pd.notna(row.ma20) else float(row.close),
                ma60=float(row.ma60) if pd.notna(row.ma60) else float(row.close),
                high60=float(row.high60) if pd.notna(row.high60) else float(row.high),
                high120=float(row.high120) if pd.notna(row.high120) else float(row.high),
                vol5=float(row.vol5) if pd.notna(row.vol5) else float(row.volume),
                vol20=float(row.vol20) if pd.notna(row.vol20) else float(row.volume),
            )
            samples.append(
                TrainingSample(
                    trade_date=pd.Timestamp(row.date).strftime("%Y-%m-%d"),
                    symbol=symbol,
                    stage=stage,
                    label=self._carry_outcome_class(forward_return=forward_return, max_drawdown=max_drawdown),
                    feature_values=features,
                    forward_return_20d=forward_return,
                    max_drawdown_20d=max_drawdown,
                    forward_return_bucket=self._forward_return_bucket(forward_return),
                    max_drawdown_bucket=self._max_drawdown_bucket(max_drawdown),
                )
            )
        return samples

    def _feature_row(
        self,
        *,
        symbol: str,
        stage: str,
        close: float,
        ret_5: float,
        ret_20: float,
        ma20: float,
        ma60: float,
        high60: float,
        high120: float,
        vol5: float,
        vol20: float,
    ) -> dict[str, float]:
        role_values = dict(self.STATIC_ROLE_FEATURES[symbol])
        vol_ratio = vol5 / vol20 if vol20 else 1.0
        relative_strength = close / ma20 - 1.0 if ma20 else 0.0
        earnings_revision_pressure = close / ma60 - 1.0 if ma60 else 0.0
        rerating_gap = 1.0 - min(close / high120, 1.0) if high120 else 0.0
        breakout_or_hold = 1.0 if close >= max(ma20, high60 * 0.97) else 0.0
        return {
            "product_price_change_proxy": ret_20,
            "demand_acceleration_proxy": ret_5 - (ret_20 / 4.0),
            "supply_tightness_proxy": vol_ratio - 1.0,
            "official_or_industry_catalyst_presence": self.STAGE_CATALYST_FLAG.get(stage, 0.0),
            "revenue_sensitivity_class": role_values["revenue_sensitivity_class"],
            "gross_margin_sensitivity_class": role_values["gross_margin_sensitivity_class"],
            "order_or_capacity_sensitivity_proxy": self.STAGE_STRENGTH.get(stage, 0.0),
            "earnings_revision_pressure_proxy": earnings_revision_pressure,
            "rerating_gap_proxy": rerating_gap,
            "relative_strength_persistence": relative_strength,
            "volume_expansion_confirmation": vol_ratio,
            "breakout_or_hold_structure": breakout_or_hold,
        }

    def _cycle_span(self, cycle_window: dict[str, str]) -> tuple[str, str]:
        months = [value for value in cycle_window.values() if value]
        return min(months), max(months)

    def _resolve_stage(self, *, cycle_window: dict[str, str], trade_date: pd.Timestamp) -> str | None:
        month = trade_date.strftime("%Y-%m")
        for stage, start_key, end_key in [
            ("first_markup", "first_markup_start", "first_markup_end"),
            ("cooling_and_box", "cooling_and_box_start", "cooling_and_box_end"),
            ("second_markup", "second_markup_start", "second_markup_end"),
            ("deep_box_reset", "deep_box_reset_start", "deep_box_reset_end"),
            ("long_box_reset", "long_box_reset_start", "long_box_reset_end"),
            ("major_markup", "major_markup_start", "major_markup_end"),
            ("high_level_consolidation", "high_level_consolidation_start", "high_level_consolidation_end"),
        ]:
            start = cycle_window.get(start_key)
            end = cycle_window.get(end_key)
            if start and end and start <= month <= end:
                return stage
        for stage, key in [("pullback", "pullback_window"), ("rebound", "rebound_window")]:
            value = cycle_window.get(key)
            if value and value == month:
                return stage
        return None

    def _forward_return_bucket(self, value: float) -> str:
        if value >= 0.20:
            return "strong_up"
        if value >= 0.08:
            return "moderate_up"
        if value > -0.05:
            return "flat_or_mixed"
        return "down"

    def _max_drawdown_bucket(self, value: float) -> str:
        if value > -0.08:
            return "contained"
        if value > -0.15:
            return "normal"
        return "severe"

    def _carry_outcome_class(self, *, forward_return: float, max_drawdown: float) -> str:
        if forward_return >= 0.15 and max_drawdown > -0.12:
            return "carry_constructive"
        if forward_return >= 0.05 and max_drawdown > -0.18:
            return "watch_constructive"
        return "failed"

    def _distribution(self, labels: list[str]) -> dict[str, int]:
        distribution: dict[str, int] = {}
        for label in labels:
            distribution[label] = distribution.get(label, 0) + 1
        return distribution


def write_v112b_baseline_readout_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BBaselineReadoutReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
