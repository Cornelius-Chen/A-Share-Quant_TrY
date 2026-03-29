from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(slots=True)
class U1LightweightGeometryReport:
    summary: dict[str, Any]
    feature_matrix: list[dict[str, Any]]
    correlation_rows: list[dict[str, Any]]
    principal_axes: list[dict[str, Any]]
    case_geometry: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_matrix": self.feature_matrix,
            "correlation_rows": self.correlation_rows,
            "principal_axes": self.principal_axes,
            "case_geometry": self.case_geometry,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class U1LightweightGeometryAnalyzer:
    """Run a small numpy-only geometry read on suspect feature rows."""

    def analyze(
        self,
        *,
        recheck_payload: dict[str, Any],
        feature_names: list[str],
    ) -> U1LightweightGeometryReport:
        raw_rows = list(recheck_payload.get("case_rows", []))
        if not raw_rows:
            raise ValueError("Recheck payload must contain non-empty case_rows.")

        matrix_rows: list[dict[str, Any]] = []
        vectors: list[list[float]] = []
        for row in raw_rows:
            feature_payload = {name: float(row.get(name, 0.0) or 0.0) for name in feature_names}
            matrix_rows.append(
                {
                    "case_name": row.get("case_name"),
                    "symbol": row.get("symbol"),
                    "trigger_date": row.get("trigger_date"),
                    "mechanism_type": row.get("mechanism_type"),
                    "features": feature_payload,
                }
            )
            vectors.append([feature_payload[name] for name in feature_names])

        matrix = np.asarray(vectors, dtype=float)
        means = matrix.mean(axis=0)
        stds = matrix.std(axis=0)
        active_mask = stds > 1e-12
        active_feature_names = [name for name, keep in zip(feature_names, active_mask) if keep]
        standardized = (matrix[:, active_mask] - means[active_mask]) / stds[active_mask]

        correlation_rows: list[dict[str, Any]] = []
        if standardized.shape[1] >= 2:
            corr = np.corrcoef(standardized, rowvar=False)
            for i in range(len(active_feature_names)):
                for j in range(i + 1, len(active_feature_names)):
                    correlation_rows.append(
                        {
                            "feature_a": active_feature_names[i],
                            "feature_b": active_feature_names[j],
                            "correlation": round(float(corr[i, j]), 6),
                        }
                    )
            correlation_rows.sort(key=lambda item: abs(item["correlation"]), reverse=True)

        u, s, vt = np.linalg.svd(standardized, full_matrices=False)
        explained = (s ** 2) / np.sum(s ** 2) if np.sum(s ** 2) > 0 else np.zeros_like(s)
        principal_axes: list[dict[str, Any]] = []
        for idx in range(min(2, vt.shape[0])):
            loadings = [
                {
                    "feature_name": feature_name,
                    "loading": round(float(loading), 6),
                }
                for feature_name, loading in zip(active_feature_names, vt[idx])
            ]
            loadings.sort(key=lambda item: abs(item["loading"]), reverse=True)
            principal_axes.append(
                {
                    "axis_name": f"pc{idx + 1}",
                    "explained_variance_ratio": round(float(explained[idx]), 6),
                    "top_loadings": loadings[:5],
                }
            )

        coordinates = standardized @ vt[:2].T if vt.shape[0] >= 2 else standardized @ vt[:1].T
        case_names = sorted({str(row.get("case_name")) for row in raw_rows})
        case_geometry: list[dict[str, Any]] = []
        centroids: dict[str, np.ndarray] = {}
        for case_name in case_names:
            case_indices = [i for i, row in enumerate(raw_rows) if str(row.get("case_name")) == case_name]
            case_coords = coordinates[case_indices]
            centroid = case_coords.mean(axis=0)
            centroids[case_name] = centroid
            case_geometry.append(
                {
                    "case_name": case_name,
                    "row_count": len(case_indices),
                    "pc1_centroid": round(float(centroid[0]), 6),
                    "pc2_centroid": round(float(centroid[1]) if centroid.shape[0] > 1 else 0.0, 6),
                    "pc_spread": round(float(np.linalg.norm(case_coords - centroid, axis=1).mean()), 6),
                }
            )

        centroid_distance = 0.0
        if len(case_names) >= 2:
            first_centroid = centroids[case_names[0]]
            second_centroid = centroids[case_names[1]]
            centroid_distance = round(float(np.linalg.norm(first_centroid - second_centroid)), 6)

        summary = {
            "case_count": len(case_names),
            "row_count": len(raw_rows),
            "active_feature_count": len(active_feature_names),
            "top_abs_correlation_pair": correlation_rows[0] if correlation_rows else None,
            "pc1_explained_variance_ratio": principal_axes[0]["explained_variance_ratio"] if principal_axes else 0.0,
            "case_centroid_distance": centroid_distance,
            "separation_reading": (
                "cases_geometrically_separable"
                if centroid_distance >= 1.0
                else "cases_only_weakly_separable"
            ),
        }
        interpretation = [
            "U1 lightweight geometry is only useful if it changes a feature-pack decision or pocket interpretation boundary.",
            "High centroid separation means the current suspects likely belong to different local-causal regimes rather than one blended feature branch.",
            "Strong principal-axis loadings highlight which current features already separate the pockets, and therefore which additional features are less likely to add decision value.",
        ]
        return U1LightweightGeometryReport(
            summary=summary,
            feature_matrix=matrix_rows,
            correlation_rows=correlation_rows[:10],
            principal_axes=principal_axes,
            case_geometry=case_geometry,
            interpretation=interpretation,
        )


def write_u1_lightweight_geometry_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: U1LightweightGeometryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
