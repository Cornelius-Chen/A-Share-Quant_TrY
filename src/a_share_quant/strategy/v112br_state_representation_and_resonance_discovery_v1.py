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

from a_share_quant.strategy.v112bp_cpo_selector_maturity_fusion_pilot_v1 import (
    V112BPCpoSelectorMaturityFusionPilotAnalyzer,
)


@dataclass(slots=True)
class V112BRStateRepresentationAndResonanceDiscoveryReport:
    summary: dict[str, Any]
    state_vector_rows: list[dict[str, Any]]
    cluster_rows: list[dict[str, Any]]
    target_mapping_rows: list[dict[str, Any]]
    resonance_bundle_rows: list[dict[str, Any]]
    veto_pocket_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "state_vector_rows": self.state_vector_rows,
            "cluster_rows": self.cluster_rows,
            "target_mapping_rows": self.target_mapping_rows,
            "resonance_bundle_rows": self.resonance_bundle_rows,
            "veto_pocket_rows": self.veto_pocket_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BRStateRepresentationAndResonanceDiscoveryAnalyzer:
    CLUSTER_COUNT = 4
    FEATURE_NAMES = [
        "ranker_score",
        "predicted_return_20d",
        "maturity_balance_score",
        "regime_support_score",
        "weighted_breadth_ratio",
        "catalyst_presence_proxy",
        "confidence_tier_numeric",
        "rollforward_state_numeric",
        "turnover_state_numeric",
        "window_uncertainty_numeric",
        "internal_turnover_concentration_state",
        "spillover_saturation_overlay_state",
        "turnover_pressure_overlay_state",
        "core_branch_relative_strength_spread_state",
        "role_deterioration_spread_state",
    ]

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        fusion_pilot_payload: dict[str, Any],
        training_layer_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112BRStateRepresentationAndResonanceDiscoveryReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112br_now")):
            raise ValueError("V1.12BR must be open before resonance discovery runs.")

        training_layer_rows = list(training_layer_payload.get("training_layer_rows", []))
        if len(training_layer_rows) != 10:
            raise ValueError("V1.12BR expects the frozen 10-row training layer.")

        bp_analyzer = V112BPCpoSelectorMaturityFusionPilotAnalyzer()
        feature_frame = bp_analyzer._build_feature_frame(  # noqa: SLF001
            training_layer_rows=training_layer_rows,
            cycle_reconstruction_payload=cycle_reconstruction_payload,
        )
        gate_rows = pd.DataFrame(list(fusion_pilot_payload.get("gate_decision_rows", [])))
        frame = gate_rows.merge(
            feature_frame[["trade_date", "symbol", "stage_family", "role_family", "catalyst_sequence_label", "forward_return_20d", "max_drawdown_20d"]],
            on=["trade_date", "symbol"],
            how="left",
        ).copy()
        if frame.empty:
            raise ValueError("V1.12BR requires non-empty fusion decision rows.")

        x = frame[self.FEATURE_NAMES].astype(float).to_numpy()
        x_mean = x.mean(axis=0)
        x_std = np.where(x.std(axis=0) == 0.0, 1.0, x.std(axis=0))
        x_scaled = (x - x_mean) / x_std

        _, _, vt = np.linalg.svd(x_scaled, full_matrices=False)
        components = vt[:3]
        embedding = x_scaled @ components.T

        labels, centers = self._kmeans(x_scaled=x_scaled, cluster_count=self.CLUSTER_COUNT)
        frame["cluster_id"] = labels
        frame["latent_x"] = embedding[:, 0]
        frame["latent_y"] = embedding[:, 1]
        frame["latent_z"] = embedding[:, 2] if embedding.shape[1] > 2 else 0.0

        cluster_rows = self._cluster_rows(frame=frame, x_scaled=x_scaled, centers=centers)
        target_mapping_rows = self._target_mapping_rows(frame=frame)
        resonance_bundle_rows = self._resonance_bundle_rows(frame=frame, x_scaled=x_scaled)
        veto_pocket_rows = self._veto_pocket_rows(frame=frame)
        state_vector_rows = self._state_vector_rows(frame=frame)

        offensive_cluster_count = sum(1 for row in target_mapping_rows if str(row["target_posture"]) == "offensive_zone")
        veto_cluster_count = sum(1 for row in target_mapping_rows if str(row["target_posture"]) == "veto_zone")
        summary = {
            "acceptance_posture": "freeze_v112br_state_representation_and_resonance_discovery_v1",
            "state_row_count": len(frame),
            "feature_dimension_count": len(self.FEATURE_NAMES),
            "latent_dimension_count": 3,
            "cluster_count": self.CLUSTER_COUNT,
            "offensive_cluster_count": offensive_cluster_count,
            "veto_cluster_count": veto_cluster_count,
            "candidate_bundle_count": len(resonance_bundle_rows),
            "candidate_veto_pocket_count": len(veto_pocket_rows),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": "map_offensive_and_veto_clusters_back_to_phase_conditioned_gate_design",
        }
        interpretation = [
            "V1.12BR does not try to explain every axis a priori. It first constructs a lawful state representation and then checks which regions line up with better or worse outcomes.",
            "The main value is not the cluster labels themselves, but the candidate offensive and veto regions they expose for later time-split rule extraction.",
        ]
        return V112BRStateRepresentationAndResonanceDiscoveryReport(
            summary=summary,
            state_vector_rows=state_vector_rows,
            cluster_rows=cluster_rows,
            target_mapping_rows=target_mapping_rows,
            resonance_bundle_rows=resonance_bundle_rows,
            veto_pocket_rows=veto_pocket_rows,
            interpretation=interpretation,
        )

    def _kmeans(self, *, x_scaled: np.ndarray, cluster_count: int) -> tuple[np.ndarray, np.ndarray]:
        seed_idx = np.linspace(0, len(x_scaled) - 1, cluster_count, dtype=int)
        centers = x_scaled[seed_idx].copy()
        labels = np.zeros(len(x_scaled), dtype=int)
        for _ in range(25):
            distances = ((x_scaled[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
            new_labels = distances.argmin(axis=1)
            if np.array_equal(new_labels, labels):
                break
            labels = new_labels
            for cluster_id in range(cluster_count):
                mask = labels == cluster_id
                if mask.any():
                    centers[cluster_id] = x_scaled[mask].mean(axis=0)
        return labels, centers

    def _cluster_rows(self, *, frame: pd.DataFrame, x_scaled: np.ndarray, centers: np.ndarray) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for cluster_id in range(self.CLUSTER_COUNT):
            cluster = frame[frame["cluster_id"] == cluster_id]
            rows.append(
                {
                    "cluster_id": int(cluster_id),
                    "row_count": int(len(cluster)),
                    "average_forward_return_20d": round(float(cluster["forward_return_20d"].mean()), 4),
                    "average_max_drawdown_20d": round(float(cluster["max_drawdown_20d"].mean()), 4),
                    "dominant_stage_family": str(cluster["stage_family"].mode().iloc[0]),
                    "dominant_role_family": str(cluster["role_family"].mode().iloc[0]),
                    "center_l2_norm": round(float(np.linalg.norm(centers[cluster_id])), 4),
                }
            )
        return rows

    def _target_mapping_rows(self, *, frame: pd.DataFrame) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for cluster_id, cluster in frame.groupby("cluster_id"):
            avg_ret = float(cluster["forward_return_20d"].mean())
            avg_dd = float(cluster["max_drawdown_20d"].mean())
            if avg_ret > 0.08 and avg_dd > -0.18:
                posture = "offensive_zone"
            elif avg_ret < 0.02 or avg_dd < -0.22:
                posture = "veto_zone"
            else:
                posture = "mixed_transition_zone"
            rows.append(
                {
                    "cluster_id": int(cluster_id),
                    "average_forward_return_20d": round(avg_ret, 4),
                    "average_max_drawdown_20d": round(avg_dd, 4),
                    "target_posture": posture,
                }
            )
        return rows

    def _resonance_bundle_rows(self, *, frame: pd.DataFrame, x_scaled: np.ndarray) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        feature_idx = {name: idx for idx, name in enumerate(self.FEATURE_NAMES)}
        for cluster_id, cluster in frame.groupby("cluster_id"):
            if float(cluster["forward_return_20d"].mean()) <= 0.08:
                continue
            cluster_scaled = x_scaled[cluster.index.to_numpy()]
            mean_vec = cluster_scaled.mean(axis=0)
            top_idx = np.argsort(np.abs(mean_vec))[::-1][:3]
            rows.append(
                {
                    "cluster_id": int(cluster_id),
                    "bundle_type": "offensive_resonance",
                    "feature_1": self.FEATURE_NAMES[int(top_idx[0])],
                    "feature_2": self.FEATURE_NAMES[int(top_idx[1])],
                    "feature_3": self.FEATURE_NAMES[int(top_idx[2])],
                    "cluster_average_forward_return_20d": round(float(cluster["forward_return_20d"].mean()), 4),
                    "cluster_average_max_drawdown_20d": round(float(cluster["max_drawdown_20d"].mean()), 4),
                }
            )
        return rows

    def _veto_pocket_rows(self, *, frame: pd.DataFrame) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for cluster_id, cluster in frame.groupby("cluster_id"):
            avg_ret = float(cluster["forward_return_20d"].mean())
            avg_dd = float(cluster["max_drawdown_20d"].mean())
            if not (avg_ret < 0.02 or avg_dd < -0.22):
                continue
            rows.append(
                {
                    "cluster_id": int(cluster_id),
                    "veto_reading": "candidate_veto_region",
                    "dominant_stage_family": str(cluster["stage_family"].mode().iloc[0]),
                    "dominant_role_family": str(cluster["role_family"].mode().iloc[0]),
                    "average_forward_return_20d": round(avg_ret, 4),
                    "average_max_drawdown_20d": round(avg_dd, 4),
                }
            )
        return rows

    def _state_vector_rows(self, *, frame: pd.DataFrame) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in frame.head(120).to_dict(orient="records"):
            rows.append(
                {
                    "trade_date": str(row["trade_date"]),
                    "symbol": str(row["symbol"]),
                    "stage_family": str(row["stage_family"]),
                    "role_family": str(row["role_family"]),
                    "cluster_id": int(row["cluster_id"]),
                    "latent_x": round(float(row["latent_x"]), 4),
                    "latent_y": round(float(row["latent_y"]), 4),
                    "latent_z": round(float(row["latent_z"]), 4),
                    "forward_return_20d": round(float(row["forward_return_20d"]), 4),
                    "max_drawdown_20d": round(float(row["max_drawdown_20d"]), 4),
                }
            )
        return rows


def write_v112br_state_representation_and_resonance_discovery_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BRStateRepresentationAndResonanceDiscoveryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
