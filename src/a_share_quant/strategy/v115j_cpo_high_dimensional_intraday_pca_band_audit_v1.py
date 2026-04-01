from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


def _to_float(value: Any, default: float = 0.0) -> float:
    text = str(value).strip()
    if text == "":
        return default
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = (len(sorted_values) - 1) * q
    low = int(pos)
    high = min(len(sorted_values) - 1, low + 1)
    frac = pos - low
    return sorted_values[low] * (1.0 - frac) + sorted_values[high] * frac


def _segment_band(value: float, *, low: float, high: float) -> str:
    if value < low:
        return "low"
    if value > high:
        return "high"
    return "mid"


def write_csv_rows(*, path: Path, rows: list[dict[str, Any]]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path


@dataclass(slots=True)
class V115JCpoHighDimensionalIntradayPcaBandAuditReport:
    summary: dict[str, Any]
    component_loading_rows: list[dict[str, Any]]
    band_context_rows: list[dict[str, Any]]
    component_context_rows: list[dict[str, Any]]
    sample_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "component_loading_rows": self.component_loading_rows,
            "band_context_rows": self.band_context_rows,
            "component_context_rows": self.component_context_rows,
            "sample_rows": self.sample_rows,
            "interpretation": self.interpretation,
        }


class V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer:
    FEATURE_COLUMNS = [
        "f30_breakout_efficiency_rz",
        "f60_breakout_efficiency_rz",
        "f30_close_vs_vwap_rz",
        "f60_close_vs_vwap_rz",
        "f30_close_location_rz",
        "f60_close_location_rz",
        "f30_pullback_from_high_rz",
        "f60_pullback_from_high_rz",
        "f30_last_bar_return_rz",
        "f60_last_bar_return_rz",
        "f30_last_bar_volume_share_rz",
        "f60_last_bar_volume_share_rz",
        "f30_high_time_ratio_rz",
        "f60_high_time_ratio_rz",
        "f30_afternoon_volume_share_rz",
        "f60_afternoon_volume_share_rz",
        "f30_upper_shadow_ratio_rz",
        "f60_upper_shadow_ratio_rz",
        "f30_lower_shadow_ratio_rz",
        "f60_lower_shadow_ratio_rz",
        "f30_body_ratio_rz",
        "f60_body_ratio_rz",
        "f30_last_bar_upper_shadow_ratio_rz",
        "f60_last_bar_upper_shadow_ratio_rz",
        "f30_last_bar_lower_shadow_ratio_rz",
        "f60_last_bar_lower_shadow_ratio_rz",
        "d5_30_close_vs_vwap_rz",
        "d15_60_close_vs_vwap_rz",
        "d5_30_last_bar_return_rz",
        "d15_60_last_bar_return_rz",
        "d5_30_last_bar_volume_share_rz",
        "d15_60_last_bar_volume_share_rz",
        "d5_30_upper_shadow_ratio_rz",
        "d15_60_upper_shadow_ratio_rz",
        "d5_30_lower_shadow_ratio_rz",
        "d15_60_lower_shadow_ratio_rz",
        "d5_30_last_bar_upper_shadow_ratio_rz",
        "d15_60_last_bar_upper_shadow_ratio_rz",
        "d5_30_last_bar_lower_shadow_ratio_rz",
        "d15_60_last_bar_lower_shadow_ratio_rz",
        "f30_failed_push_proxy",
        "f60_failed_push_proxy",
        "d15_60_failed_push_proxy",
    ]
    COMPONENT_COUNT = 3

    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self, *, training_view_rows: list[dict[str, Any]]) -> tuple[V115JCpoHighDimensionalIntradayPcaBandAuditReport, list[dict[str, Any]]]:
        rows = [dict(row) for row in training_view_rows]
        train_rows = [row for row in rows if str(row.get("split_group")) == "train"]
        test_rows = [row for row in rows if str(row.get("split_group")) == "test"]

        x_train = np.array(
            [[_to_float(row.get(feature)) for feature in self.FEATURE_COLUMNS] for row in train_rows],
            dtype=float,
        )
        feature_mean = x_train.mean(axis=0)
        x_centered = x_train - feature_mean
        _, singular_values, vt = np.linalg.svd(x_centered, full_matrices=False)
        components = vt[: self.COMPONENT_COUNT]
        explained_variance = (singular_values ** 2) / max(len(train_rows) - 1, 1)
        explained_ratio = explained_variance / max(np.sum(explained_variance), 1e-12)

        component_loading_rows: list[dict[str, Any]] = []
        for component_index in range(self.COMPONENT_COUNT):
            loadings = components[component_index]
            ranked = sorted(
                zip(self.FEATURE_COLUMNS, loadings),
                key=lambda item: abs(float(item[1])),
                reverse=True,
            )
            for feature_name, loading in ranked[:10]:
                component_loading_rows.append(
                    {
                        "component_name": f"pc{component_index + 1}",
                        "feature_name": feature_name,
                        "loading": round(float(loading), 6),
                        "absolute_loading": round(abs(float(loading)), 6),
                    }
                )

        for row in rows:
            vector = np.array([_to_float(row.get(feature)) for feature in self.FEATURE_COLUMNS], dtype=float)
            centered = vector - feature_mean
            scores = components @ centered
            for component_index in range(self.COMPONENT_COUNT):
                row[f"pc{component_index + 1}_score"] = round(float(scores[component_index]), 6)

        pc1_train_values = sorted(_to_float(row.get("pc1_score")) for row in train_rows)
        pc2_train_values = sorted(_to_float(row.get("pc2_score")) for row in train_rows)
        pc1_low = _quantile(pc1_train_values, 0.33)
        pc1_high = _quantile(pc1_train_values, 0.67)
        pc2_low = _quantile(pc2_train_values, 0.33)
        pc2_high = _quantile(pc2_train_values, 0.67)

        for row in rows:
            row["pc1_band"] = _segment_band(_to_float(row.get("pc1_score")), low=pc1_low, high=pc1_high)
            row["pc2_band"] = _segment_band(_to_float(row.get("pc2_score")), low=pc2_low, high=pc2_high)
            row["state_band"] = f"pc1_{row['pc1_band']}__pc2_{row['pc2_band']}"

        band_context_rows: list[dict[str, Any]] = []
        state_bands = sorted({str(row["state_band"]) for row in rows})
        for state_band in state_bands:
            band_rows = [row for row in rows if str(row["state_band"]) == state_band]
            band_context_rows.append(
                {
                    "state_band": state_band,
                    "row_count": len(band_rows),
                    "increase_rate": round(_mean([1.0 if str(row.get("coarse_label")) == "increase_expression" else 0.0 for row in band_rows]), 6),
                    "decrease_rate": round(_mean([1.0 if str(row.get("coarse_label")) == "decrease_expression" else 0.0 for row in band_rows]), 6),
                    "hold_rate": round(_mean([1.0 if str(row.get("coarse_label")) == "hold_or_skip" else 0.0 for row in band_rows]), 6),
                    "avg_expectancy_proxy_3d": round(_mean([_to_float(row.get("expectancy_proxy_3d")) for row in band_rows]), 6),
                    "avg_max_adverse_return_3d": round(_mean([_to_float(row.get("max_adverse_return_3d")) for row in band_rows]), 6),
                }
            )
        band_context_rows.sort(key=lambda row: (float(row["increase_rate"]), float(row["avg_expectancy_proxy_3d"])), reverse=True)

        component_context_rows = []
        for context in sorted({str(row["coarse_label"]) for row in rows}):
            context_rows = [row for row in rows if str(row["coarse_label"]) == context]
            component_context_rows.append(
                {
                    "coarse_label": context,
                    "row_count": len(context_rows),
                    "pc1_mean": round(_mean([_to_float(row.get("pc1_score")) for row in context_rows]), 6),
                    "pc2_mean": round(_mean([_to_float(row.get("pc2_score")) for row in context_rows]), 6),
                    "pc3_mean": round(_mean([_to_float(row.get("pc3_score")) for row in context_rows]), 6),
                    "avg_expectancy_proxy_3d": round(_mean([_to_float(row.get("expectancy_proxy_3d")) for row in context_rows]), 6),
                }
            )

        best_band = band_context_rows[0] if band_context_rows else {}
        summary = {
            "acceptance_posture": "freeze_v115j_cpo_high_dimensional_intraday_pca_band_audit_v1",
            "base_row_count": len(rows),
            "train_row_count": len(train_rows),
            "test_row_count": len(test_rows),
            "feature_count": len(self.FEATURE_COLUMNS),
            "component_count": self.COMPONENT_COUNT,
            "pc1_explained_ratio": round(float(explained_ratio[0]), 6) if len(explained_ratio) > 0 else 0.0,
            "pc2_explained_ratio": round(float(explained_ratio[1]), 6) if len(explained_ratio) > 1 else 0.0,
            "pc3_explained_ratio": round(float(explained_ratio[2]), 6) if len(explained_ratio) > 2 else 0.0,
            "best_state_band": best_band.get("state_band"),
            "best_state_band_increase_rate": best_band.get("increase_rate"),
            "best_state_band_avg_expectancy_proxy_3d": best_band.get("avg_expectancy_proxy_3d"),
            "discovery_posture": "continuous_band_audit_before_discrete_clustering",
            "candidate_only_pilot": True,
            "recommended_next_posture": "use_v115j_to_filter_candidate_add_bands_then_decide_whether_discrete_clustering_is_even_necessary",
        }
        interpretation = [
            "V1.15J is the first unsupervised-style audit on the V115H high-dimensional intraday base table, but it intentionally stops at PCA bands rather than hard clusters.",
            "The project is checking whether the strongest directions in the discovery space align with action-expression differences before committing to any clustering law.",
            "If the continuous bands already show useful action separation, that is preferable to forcing discrete clusters onto what may actually be a smooth state manifold.",
        ]
        report = V115JCpoHighDimensionalIntradayPcaBandAuditReport(
            summary=summary,
            component_loading_rows=component_loading_rows,
            band_context_rows=band_context_rows,
            component_context_rows=component_context_rows,
            sample_rows=rows[:10],
            interpretation=interpretation,
        )
        return report, rows


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V115JCpoHighDimensionalIntradayPcaBandAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    with (repo_root / "data" / "training" / "cpo_midfreq_high_dimensional_action_training_view_v1.csv").open("r", encoding="utf-8") as handle:
        training_view_rows = list(csv.DictReader(handle))
    analyzer = V115JCpoHighDimensionalIntradayPcaBandAuditAnalyzer(repo_root=repo_root)
    result, annotated_rows = analyzer.analyze(training_view_rows=training_view_rows)
    write_csv_rows(
        path=repo_root / "data" / "training" / "cpo_midfreq_pca_band_rows_v1.csv",
        rows=annotated_rows,
    )
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v115j_cpo_high_dimensional_intraday_pca_band_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
