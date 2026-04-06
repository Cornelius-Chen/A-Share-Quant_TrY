from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v122_1min_label_plane_utils import load_recent_1min_labeled_rows


POSITIVE_LABELS = {"reduce_probe", "close_probe"}


def zscore(values: list[float]) -> np.ndarray:
    array = np.asarray(values, dtype=float)
    std = float(array.std())
    if std == 0.0:
        std = 1.0
    return (array - float(array.mean())) / std


def balanced_accuracy(y_true: list[bool], y_pred: list[bool]) -> float:
    positives = [idx for idx, value in enumerate(y_true) if value]
    negatives = [idx for idx, value in enumerate(y_true) if not value]
    pos_recall = sum(y_pred[idx] for idx in positives) / len(positives) if positives else 0.0
    neg_recall = sum((not y_pred[idx]) for idx in negatives) / len(negatives) if negatives else 0.0
    return (pos_recall + neg_recall) / 2.0


def load_recent_1min_downside_rows(repo_root: Path) -> list[dict[str, Any]]:
    rows = load_recent_1min_labeled_rows(repo_root)

    burst_z = zscore([float(row["burst_then_fade_score"]) for row in rows])
    upper_shadow_z = zscore([float(row["upper_shadow_pct"]) for row in rows])
    pullback_z = zscore([float(row["micro_pullback_depth"]) for row in rows])
    push_z = zscore([float(row["push_efficiency"]) for row in rows])
    late_z = zscore([float(row["late_session_integrity_score"]) for row in rows])
    close_location_z = zscore([float(row["close_location"]) for row in rows])
    reclaim_z = zscore([float(row["reclaim_after_break_score"]) for row in rows])
    abs_close_vs_vwap_z = zscore([abs(float(row["close_vs_vwap"])) for row in rows])

    value_ratio_z = zscore([float(row["value_ratio_5"]) for row in rows])
    range_pct_z = zscore([float(row["range_pct"]) for row in rows])
    body_pct_z = zscore([float(row["body_pct"]) for row in rows])
    lower_shadow_z = zscore([float(row["lower_shadow_pct"]) for row in rows])
    prev_gap_z = zscore([float(row["prev_close_gap"]) for row in rows])
    close_vs_vwap_z = zscore([float(row["close_vs_vwap"]) for row in rows])
    volume_ratio_z = zscore([float(row["volume_ratio_5"]) for row in rows])

    candidate_columns: dict[str, np.ndarray] = {
        "downside_failure_score": (
            0.26 * burst_z
            + 0.18 * upper_shadow_z
            + 0.16 * pullback_z
            - 0.14 * push_z
            - 0.12 * late_z
            - 0.08 * close_location_z
            - 0.04 * reclaim_z
            + 0.02 * abs_close_vs_vwap_z
        ),
        "churn_rejection_score": (
            0.24 * volume_ratio_z
            + 0.20 * value_ratio_z
            + 0.18 * range_pct_z
            + 0.14 * upper_shadow_z
            - 0.12 * body_pct_z
            - 0.08 * lower_shadow_z
            - 0.04 * close_vs_vwap_z
        ),
        "vwap_rejection_imbalance_score": (
            0.28 * abs_close_vs_vwap_z
            - 0.22 * close_vs_vwap_z
            + 0.18 * upper_shadow_z
            + 0.12 * value_ratio_z
            - 0.10 * lower_shadow_z
            - 0.10 * body_pct_z
        ),
        "gap_exhaustion_stall_score": (
            0.26 * prev_gap_z
            + 0.18 * range_pct_z
            + 0.16 * value_ratio_z
            + 0.14 * upper_shadow_z
            - 0.14 * body_pct_z
            - 0.12 * lower_shadow_z
        ),
    }

    for name, values in candidate_columns.items():
        for index, row in enumerate(rows):
            row[name] = float(values[index])

    return rows

