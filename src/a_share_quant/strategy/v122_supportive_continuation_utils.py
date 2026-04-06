from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np


FEATURE_COLUMNS = [
    "minute_return",
    "range_pct",
    "body_pct",
    "upper_shadow_pct",
    "lower_shadow_pct",
    "close_location",
    "close_vs_vwap",
    "pullback_from_high",
    "push_efficiency",
    "micro_pullback_depth",
    "volume_ratio_5",
    "value_ratio_5",
    "prev_close_gap",
    "reclaim_after_break_score",
    "burst_then_fade_score",
    "late_session_integrity_score",
]
HORIZON = 5


def _band(value: float, q_low: float, q_high: float) -> str:
    if value <= q_low:
        return "low"
    if value >= q_high:
        return "high"
    return "mid"


def _zscore(values: list[float]) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    mean = float(array.mean())
    std = float(array.std())
    if std == 0.0:
        std = 1.0
    return (array - mean) / std


def load_supportive_continuation_rows(repo_root: Path) -> list[dict[str, Any]]:
    training_path = repo_root / "data" / "training" / "cpo_recent_1min_microstructure_feature_table_v1.csv"
    with training_path.open("r", encoding="utf-8") as handle:
        base_rows = list(csv.DictReader(handle))

    matrix = np.array([[float(row[column]) for column in FEATURE_COLUMNS] for row in base_rows], dtype=float)
    means = matrix.mean(axis=0)
    stds = matrix.std(axis=0)
    stds[stds == 0.0] = 1.0
    standardized = (matrix - means) / stds
    covariance = np.cov(standardized, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvectors = eigenvectors[:, order]
    projection = standardized @ eigenvectors[:, :2]
    pc1_values = projection[:, 0]
    pc2_values = projection[:, 1]
    pc1_q_low, pc1_q_high = np.quantile(pc1_values, [1 / 3, 2 / 3])
    pc2_q_low, pc2_q_high = np.quantile(pc2_values, [1 / 3, 2 / 3])

    family_path = repo_root / "reports" / "analysis" / "v121y_cpo_recent_1min_supportive_continuation_candidate_discovery_v1.json"
    with family_path.open("r", encoding="utf-8") as handle:
        family_report = json.load(handle)
    supportive_bands = set(family_report["summary"]["candidate_band_names"])

    grouped_indices: dict[tuple[str, str], list[int]] = {}
    for index, row in enumerate(base_rows):
        band_name = f"pc1_{_band(pc1_values[index], pc1_q_low, pc1_q_high)}__pc2_{_band(pc2_values[index], pc2_q_low, pc2_q_high)}"
        if band_name not in supportive_bands:
            continue
        grouped_indices.setdefault((row["symbol"], row["trade_date"]), []).append(index)

    supportive_rows: list[dict[str, Any]] = []
    for (_symbol, _trade_date), indices in grouped_indices.items():
        for local_position, index in enumerate(indices):
            if local_position + HORIZON >= len(indices):
                continue
            row = base_rows[index]
            current_close = float(row["close"])
            future_indices = indices[local_position + 1 : local_position + HORIZON + 1]
            future_rows = [base_rows[item] for item in future_indices]
            future_close = float(future_rows[-1]["close"])
            future_high = max(float(item["high"]) for item in future_rows)
            future_low = min(float(item["low"]) for item in future_rows)
            supportive_rows.append(
                {
                    "symbol": row["symbol"],
                    "trade_date": row["trade_date"],
                    "clock_time": row["clock_time"],
                    "close_location": float(row["close_location"]),
                    "close_vs_vwap": float(row["close_vs_vwap"]),
                    "push_efficiency": float(row["push_efficiency"]),
                    "reclaim_after_break_score": float(row["reclaim_after_break_score"]),
                    "upper_shadow_pct": float(row["upper_shadow_pct"]),
                    "micro_pullback_depth": float(row["micro_pullback_depth"]),
                    "burst_then_fade_score": float(row["burst_then_fade_score"]),
                    "late_session_integrity_score": float(row["late_session_integrity_score"]),
                    "forward_return_5": future_close / current_close - 1.0,
                    "max_favorable_return_5": future_high / current_close - 1.0,
                    "max_adverse_return_5": future_low / current_close - 1.0,
                }
            )

    if not supportive_rows:
        fallback_grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in base_rows:
            if (
                float(row["push_efficiency"]) > 0.5
                and float(row["late_session_integrity_score"]) > 0.08
                and float(row["close_vs_vwap"]) > -0.0095
            ):
                fallback_grouped.setdefault((row["symbol"], row["trade_date"]), []).append(row)

        for (_symbol, _trade_date), items in fallback_grouped.items():
            for local_position, row in enumerate(items):
                if local_position + HORIZON >= len(items):
                    continue
                current_close = float(row["close"])
                future_rows = items[local_position + 1 : local_position + HORIZON + 1]
                future_close = float(future_rows[-1]["close"])
                future_high = max(float(item["high"]) for item in future_rows)
                future_low = min(float(item["low"]) for item in future_rows)
                supportive_rows.append(
                    {
                        "symbol": row["symbol"],
                        "trade_date": row["trade_date"],
                        "clock_time": row["clock_time"],
                        "close_location": float(row["close_location"]),
                        "close_vs_vwap": float(row["close_vs_vwap"]),
                        "push_efficiency": float(row["push_efficiency"]),
                        "reclaim_after_break_score": float(row["reclaim_after_break_score"]),
                        "upper_shadow_pct": float(row["upper_shadow_pct"]),
                        "micro_pullback_depth": float(row["micro_pullback_depth"]),
                        "burst_then_fade_score": float(row["burst_then_fade_score"]),
                        "late_session_integrity_score": float(row["late_session_integrity_score"]),
                        "forward_return_5": future_close / current_close - 1.0,
                        "max_favorable_return_5": future_high / current_close - 1.0,
                        "max_adverse_return_5": future_low / current_close - 1.0,
                    }
                )

    if not supportive_rows:
        return []

    push_z = _zscore([row["push_efficiency"] for row in supportive_rows])
    late_z = _zscore([row["late_session_integrity_score"] for row in supportive_rows])
    reclaim_z = _zscore([row["reclaim_after_break_score"] for row in supportive_rows])
    close_loc_z = _zscore([row["close_location"] for row in supportive_rows])
    abs_close_vs_vwap_z = _zscore([abs(row["close_vs_vwap"]) for row in supportive_rows])
    upper_shadow_z = _zscore([row["upper_shadow_pct"] for row in supportive_rows])
    burst_fade_z = _zscore([row["burst_then_fade_score"] for row in supportive_rows])
    pullback_z = _zscore([row["micro_pullback_depth"] for row in supportive_rows])

    for index, row in enumerate(supportive_rows):
        row["supportive_quality_score"] = float(
            0.28 * push_z[index]
            + 0.24 * late_z[index]
            + 0.18 * reclaim_z[index]
            + 0.12 * close_loc_z[index]
            - 0.10 * abs_close_vs_vwap_z[index]
            - 0.04 * upper_shadow_z[index]
            - 0.02 * burst_fade_z[index]
            - 0.02 * pullback_z[index]
        )
        row["positive_forward_5"] = row["forward_return_5"] > 0.0
    return supportive_rows
