from __future__ import annotations

import csv
import json
from dataclasses import dataclass
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


def _band(value: float, q_low: float, q_high: float) -> str:
    if value <= q_low:
        return "low"
    if value >= q_high:
        return "high"
    return "mid"


@dataclass(slots=True)
class V121XCpoRecent1MinPcaStructureAuditReport:
    summary: dict[str, Any]
    component_rows: list[dict[str, Any]]
    band_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "component_rows": self.component_rows,
            "band_rows": self.band_rows,
            "interpretation": self.interpretation,
        }


class V121XCpoRecent1MinPcaStructureAuditAnalyzer:
    def __init__(self, *, repo_root: Path) -> None:
        self.repo_root = repo_root

    def analyze(self) -> V121XCpoRecent1MinPcaStructureAuditReport:
        feature_table = self.repo_root / "data" / "training" / "cpo_recent_1min_microstructure_feature_table_v1.csv"
        with feature_table.open("r", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))

        matrix = np.array([[float(row[column]) for column in FEATURE_COLUMNS] for row in rows], dtype=float)
        means = matrix.mean(axis=0)
        stds = matrix.std(axis=0)
        stds[stds == 0.0] = 1.0
        standardized = (matrix - means) / stds

        covariance = np.cov(standardized, rowvar=False)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance)
        order = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[order]
        eigenvectors = eigenvectors[:, order]
        explained = eigenvalues / eigenvalues.sum()
        projection = standardized @ eigenvectors[:, :2]

        pc1_values = projection[:, 0]
        pc2_values = projection[:, 1]
        pc1_q_low, pc1_q_high = np.quantile(pc1_values, [1 / 3, 2 / 3])
        pc2_q_low, pc2_q_high = np.quantile(pc2_values, [1 / 3, 2 / 3])

        bands: dict[str, dict[str, float]] = {}
        for index, row in enumerate(rows):
            key = f"pc1_{_band(pc1_values[index], pc1_q_low, pc1_q_high)}__pc2_{_band(pc2_values[index], pc2_q_low, pc2_q_high)}"
            band_state = bands.setdefault(
                key,
                {
                    "row_count": 0,
                    "mean_close_vs_vwap": 0.0,
                    "mean_push_efficiency": 0.0,
                    "mean_burst_then_fade_score": 0.0,
                    "mean_late_session_integrity_score": 0.0,
                },
            )
            band_state["row_count"] += 1
            band_state["mean_close_vs_vwap"] += float(row["close_vs_vwap"])
            band_state["mean_push_efficiency"] += float(row["push_efficiency"])
            band_state["mean_burst_then_fade_score"] += float(row["burst_then_fade_score"])
            band_state["mean_late_session_integrity_score"] += float(row["late_session_integrity_score"])

        band_rows = []
        for band_name, metrics in sorted(bands.items()):
            row_count = metrics["row_count"]
            band_rows.append(
                {
                    "band": band_name,
                    "row_count": row_count,
                    "mean_close_vs_vwap": round(metrics["mean_close_vs_vwap"] / row_count, 8),
                    "mean_push_efficiency": round(metrics["mean_push_efficiency"] / row_count, 8),
                    "mean_burst_then_fade_score": round(metrics["mean_burst_then_fade_score"] / row_count, 8),
                    "mean_late_session_integrity_score": round(
                        metrics["mean_late_session_integrity_score"] / row_count,
                        8,
                    ),
                }
            )

        component_rows = []
        for component_index in range(2):
            loadings = [
                {
                    "feature": feature,
                    "loading": round(float(eigenvectors[feature_index, component_index]), 8),
                    "abs_loading": round(abs(float(eigenvectors[feature_index, component_index])), 8),
                }
                for feature_index, feature in enumerate(FEATURE_COLUMNS)
            ]
            loadings.sort(key=lambda item: item["abs_loading"], reverse=True)
            component_rows.append(
                {
                    "component": f"pc{component_index + 1}",
                    "explained_ratio": round(float(explained[component_index]), 8),
                    "top_loadings": loadings[:5],
                }
            )

        summary = {
            "acceptance_posture": "freeze_v121x_cpo_recent_1min_pca_structure_audit_v1",
            "row_count": int(matrix.shape[0]),
            "feature_count": int(matrix.shape[1]),
            "pc1_explained_ratio": round(float(explained[0]), 8),
            "pc2_explained_ratio": round(float(explained[1]), 8),
            "band_count": len(band_rows),
            "recommended_next_posture": "derive_1min_candidate_microstructure_families_from_pc_structure",
        }
        interpretation = [
            "V1.21X turns the recent 1-minute feature table into a concrete high-dimensional structure audit instead of hand-defining a new family first.",
            "The immediate value is identifying dominant microstructure axes and continuous bands before any replay-facing use.",
            "The next step is to derive one or two candidate 1-minute families from this structure and audit them adversarially.",
        ]
        return V121XCpoRecent1MinPcaStructureAuditReport(
            summary=summary,
            component_rows=component_rows,
            band_rows=band_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V121XCpoRecent1MinPcaStructureAuditReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    analyzer = V121XCpoRecent1MinPcaStructureAuditAnalyzer(repo_root=repo_root)
    result = analyzer.analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v121x_cpo_recent_1min_pca_structure_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
