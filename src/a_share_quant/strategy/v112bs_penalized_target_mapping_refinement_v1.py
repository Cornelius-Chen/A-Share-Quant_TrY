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
from a_share_quant.strategy.v112br_state_representation_and_resonance_discovery_v1 import (
    V112BRStateRepresentationAndResonanceDiscoveryAnalyzer,
)


@dataclass(slots=True)
class V112BSPenalizedTargetMappingRefinementReport:
    summary: dict[str, Any]
    penalized_cluster_rows: list[dict[str, Any]]
    veto_neighborhood_rows: list[dict[str, Any]]
    transition_band_rows: list[dict[str, Any]]
    candidate_bundle_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "penalized_cluster_rows": self.penalized_cluster_rows,
            "veto_neighborhood_rows": self.veto_neighborhood_rows,
            "transition_band_rows": self.transition_band_rows,
            "candidate_bundle_rows": self.candidate_bundle_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BSPenalizedTargetMappingRefinementAnalyzer:
    CLUSTER_COUNT = 4
    FEATURE_NAMES = V112BRStateRepresentationAndResonanceDiscoveryAnalyzer.FEATURE_NAMES
    NEIGHBOR_COUNT = 12

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        fusion_pilot_payload: dict[str, Any],
        training_layer_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> V112BSPenalizedTargetMappingRefinementReport:
        if not bool(dict(phase_charter_payload.get("summary", {})).get("do_open_v112bs_now")):
            raise ValueError("V1.12BS must be open before the penalized target mapping refinement runs.")

        frame, embedding, centers = self._build_state_frame(
            fusion_pilot_payload=fusion_pilot_payload,
            training_layer_payload=training_layer_payload,
            cycle_reconstruction_payload=cycle_reconstruction_payload,
        )

        frame = self._attach_penalties(frame=frame, embedding=embedding, centers=centers)
        penalized_cluster_rows = self._penalized_cluster_rows(frame=frame)
        veto_neighborhood_rows = self._veto_neighborhood_rows(frame=frame, embedding=embedding)
        transition_band_rows = self._transition_band_rows(frame=frame)
        candidate_bundle_rows = self._candidate_bundle_rows(frame=frame)

        candidate_veto_cluster_count = sum(
            1 for row in penalized_cluster_rows if str(row["penalized_posture"]) == "candidate_veto_cluster"
        )
        summary = {
            "acceptance_posture": "freeze_v112bs_penalized_target_mapping_refinement_v1",
            "state_row_count": int(len(frame)),
            "feature_dimension_count": len(self.FEATURE_NAMES),
            "cluster_count": self.CLUSTER_COUNT,
            "candidate_veto_cluster_count": candidate_veto_cluster_count,
            "candidate_veto_neighborhood_count": len(veto_neighborhood_rows),
            "candidate_transition_band_count": len(transition_band_rows),
            "candidate_bundle_count": len(candidate_bundle_rows),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "ready_for_phase_check_next": True,
            "recommended_next_posture": (
                "map_penalized_veto_regions_back_to_phase_conditioned_veto_and_eligibility_design"
            ),
        }
        interpretation = [
            "V1.12BS keeps the high-dimensional state representation fixed and only refines how danger is made visible.",
            "Risk structure is allowed to surface as clusters, local neighborhoods, or transition bands instead of forcing it into a single clean bad cluster.",
        ]
        return V112BSPenalizedTargetMappingRefinementReport(
            summary=summary,
            penalized_cluster_rows=penalized_cluster_rows,
            veto_neighborhood_rows=veto_neighborhood_rows,
            transition_band_rows=transition_band_rows,
            candidate_bundle_rows=candidate_bundle_rows,
            interpretation=interpretation,
        )

    def _build_state_frame(
        self,
        *,
        fusion_pilot_payload: dict[str, Any],
        training_layer_payload: dict[str, Any],
        cycle_reconstruction_payload: dict[str, Any],
    ) -> tuple[pd.DataFrame, np.ndarray, np.ndarray]:
        training_layer_rows = list(training_layer_payload.get("training_layer_rows", []))
        if len(training_layer_rows) != 10:
            raise ValueError("V1.12BS expects the frozen 10-row training layer.")

        bp_analyzer = V112BPCpoSelectorMaturityFusionPilotAnalyzer()
        feature_frame = bp_analyzer._build_feature_frame(  # noqa: SLF001
            training_layer_rows=training_layer_rows,
            cycle_reconstruction_payload=cycle_reconstruction_payload,
        )
        gate_rows = pd.DataFrame(list(fusion_pilot_payload.get("gate_decision_rows", [])))
        frame = gate_rows.merge(
            feature_frame[
                [
                    "trade_date",
                    "symbol",
                    "stage_family",
                    "role_family",
                    "catalyst_sequence_label",
                    "forward_return_20d",
                    "max_drawdown_20d",
                ]
            ],
            on=["trade_date", "symbol"],
            how="left",
        ).copy()
        if frame.empty:
            raise ValueError("V1.12BS requires non-empty fusion decision rows.")

        x = frame[self.FEATURE_NAMES].astype(float).to_numpy()
        x_mean = x.mean(axis=0)
        x_std = np.where(x.std(axis=0) == 0.0, 1.0, x.std(axis=0))
        x_scaled = (x - x_mean) / x_std

        _, _, vt = np.linalg.svd(x_scaled, full_matrices=False)
        components = vt[:3]
        embedding = x_scaled @ components.T

        br_analyzer = V112BRStateRepresentationAndResonanceDiscoveryAnalyzer()
        labels, _ = br_analyzer._kmeans(x_scaled=x_scaled, cluster_count=self.CLUSTER_COUNT)  # noqa: SLF001
        frame["cluster_id"] = labels
        frame["latent_x"] = embedding[:, 0]
        frame["latent_y"] = embedding[:, 1]
        frame["latent_z"] = embedding[:, 2] if embedding.shape[1] > 2 else 0.0
        center_rows = []
        for cluster_id in range(self.CLUSTER_COUNT):
            mask = labels == cluster_id
            if mask.any():
                center_rows.append(embedding[mask].mean(axis=0))
            else:
                center_rows.append(np.zeros(embedding.shape[1]))
        centers = np.vstack(center_rows)
        return frame.reset_index(drop=True), embedding, centers

    def _attach_penalties(self, *, frame: pd.DataFrame, embedding: np.ndarray, centers: np.ndarray) -> pd.DataFrame:
        result = frame.copy()

        downside_return_penalty = np.clip(-result["forward_return_20d"].astype(float), 0.0, None)
        drawdown_tail_penalty = np.clip(np.abs(result["max_drawdown_20d"].astype(float)) - 0.18, 0.0, None)
        bad_trade_flag = (
            (result["forward_return_20d"].astype(float) < 0.0)
            | (result["max_drawdown_20d"].astype(float) <= -0.22)
        ).astype(float)
        bad_trade_severity = downside_return_penalty + 0.7 * drawdown_tail_penalty

        structure_penalty = (
            0.30 * np.clip(result["spillover_saturation_overlay_state"].astype(float), 0.0, None)
            + 0.22 * np.clip(result["internal_turnover_concentration_state"].astype(float) - 0.55, 0.0, None)
            + 0.18 * np.clip(result["role_deterioration_spread_state"].astype(float), 0.0, None)
            + 0.16 * np.clip(result["internal_breadth_compression_state"].astype(float) - 0.45, 0.0, None)
            + 0.08 * np.clip(result["leader_absorption_fragility_state"].astype(float), 0.0, None)
            + 0.06 * np.clip(result["branch_promotion_failure_rate_state"].astype(float) - 0.35, 0.0, None)
        )
        offensive_credit = np.clip(result["forward_return_20d"].astype(float), 0.0, None) * 0.18

        result["bad_trade_flag"] = bad_trade_flag
        result["bad_trade_severity"] = bad_trade_severity
        result["drawdown_tail_penalty"] = drawdown_tail_penalty
        result["structure_penalty"] = structure_penalty
        result["penalized_veto_intensity"] = (
            0.46 * bad_trade_flag
            + 0.28 * bad_trade_severity
            + 0.18 * drawdown_tail_penalty
            + 0.20 * structure_penalty
            - offensive_credit
        )

        distances = ((embedding[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2) ** 0.5
        sorted_distances = np.sort(distances, axis=1)
        result["boundary_margin"] = sorted_distances[:, 1] - sorted_distances[:, 0]
        result["boundary_risk_score"] = (
            result["penalized_veto_intensity"].astype(float)
            + np.clip(0.35 - result["boundary_margin"].astype(float), 0.0, None)
        )
        return result

    def _penalized_cluster_rows(self, *, frame: pd.DataFrame) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for cluster_id, cluster in frame.groupby("cluster_id"):
            avg_ret = float(cluster["forward_return_20d"].mean())
            avg_dd = float(cluster["max_drawdown_20d"].mean())
            avg_intensity = float(cluster["penalized_veto_intensity"].mean())
            bad_trade_density = float(cluster["bad_trade_flag"].mean())
            tail_density = float((cluster["max_drawdown_20d"].astype(float) <= -0.22).mean())
            if avg_intensity >= 0.30 and (bad_trade_density >= 0.40 or tail_density >= 0.28):
                posture = "candidate_veto_cluster"
            elif avg_ret >= 0.08 and avg_dd >= -0.18 and avg_intensity < 0.22:
                posture = "offensive_cluster"
            else:
                posture = "mixed_risk_transition"
            rows.append(
                {
                    "cluster_id": int(cluster_id),
                    "row_count": int(len(cluster)),
                    "average_forward_return_20d": round(avg_ret, 4),
                    "average_max_drawdown_20d": round(avg_dd, 4),
                    "average_penalized_veto_intensity": round(avg_intensity, 4),
                    "bad_trade_density": round(bad_trade_density, 4),
                    "tail_loss_density": round(tail_density, 4),
                    "dominant_stage_family": str(cluster["stage_family"].mode().iloc[0]),
                    "dominant_role_family": str(cluster["role_family"].mode().iloc[0]),
                    "penalized_posture": posture,
                }
            )
        return rows

    def _veto_neighborhood_rows(self, *, frame: pd.DataFrame, embedding: np.ndarray) -> list[dict[str, Any]]:
        distances = ((embedding[:, None, :] - embedding[None, :, :]) ** 2).sum(axis=2) ** 0.5
        np.fill_diagonal(distances, np.inf)
        local_rows: list[dict[str, Any]] = []
        for idx, row in frame.iterrows():
            neighbor_idx = np.argsort(distances[idx])[: self.NEIGHBOR_COUNT]
            neighborhood = frame.iloc[neighbor_idx]
            local_rows.append(
                {
                    "trade_date": str(row["trade_date"]),
                    "symbol": str(row["symbol"]),
                    "stage_family": str(row["stage_family"]),
                    "role_family": str(row["role_family"]),
                    "local_bad_trade_density": float(neighborhood["bad_trade_flag"].mean()),
                    "local_average_max_drawdown_20d": float(neighborhood["max_drawdown_20d"].mean()),
                    "local_average_penalized_veto_intensity": float(neighborhood["penalized_veto_intensity"].mean()),
                }
            )
        local_frame = pd.DataFrame(local_rows)
        threshold = float(local_frame["local_average_penalized_veto_intensity"].quantile(0.9))
        selected = local_frame[
            (local_frame["local_average_penalized_veto_intensity"] >= threshold)
            & (
                (local_frame["local_bad_trade_density"] >= 0.45)
                | (local_frame["local_average_max_drawdown_20d"] <= -0.18)
            )
        ].copy()
        selected = selected.sort_values(
            ["local_average_penalized_veto_intensity", "local_bad_trade_density"],
            ascending=[False, False],
        ).head(12)
        rows: list[dict[str, Any]] = []
        for pocket_id, record in enumerate(selected.to_dict(orient="records"), start=1):
            rows.append(
                {
                    "neighborhood_id": int(pocket_id),
                    "trade_date": str(record["trade_date"]),
                    "symbol": str(record["symbol"]),
                    "stage_family": str(record["stage_family"]),
                    "role_family": str(record["role_family"]),
                    "local_bad_trade_density": round(float(record["local_bad_trade_density"]), 4),
                    "local_average_max_drawdown_20d": round(float(record["local_average_max_drawdown_20d"]), 4),
                    "local_average_penalized_veto_intensity": round(float(record["local_average_penalized_veto_intensity"]), 4),
                    "pocket_reading": "candidate_veto_neighborhood",
                }
            )
        return rows

    def _transition_band_rows(self, *, frame: pd.DataFrame) -> list[dict[str, Any]]:
        margin_cut = float(frame["boundary_margin"].quantile(0.2))
        intensity_cut = float(frame["penalized_veto_intensity"].quantile(0.8))
        selected = frame[
            (frame["boundary_margin"].astype(float) <= margin_cut)
            & (frame["penalized_veto_intensity"].astype(float) >= intensity_cut)
        ].copy()
        selected = selected.sort_values(
            ["boundary_risk_score", "penalized_veto_intensity"],
            ascending=[False, False],
        ).head(12)
        rows: list[dict[str, Any]] = []
        for band_id, record in enumerate(selected.to_dict(orient="records"), start=1):
            rows.append(
                {
                    "transition_band_id": int(band_id),
                    "trade_date": str(record["trade_date"]),
                    "symbol": str(record["symbol"]),
                    "stage_family": str(record["stage_family"]),
                    "role_family": str(record["role_family"]),
                    "cluster_id": int(record["cluster_id"]),
                    "boundary_margin": round(float(record["boundary_margin"]), 4),
                    "penalized_veto_intensity": round(float(record["penalized_veto_intensity"]), 4),
                    "boundary_risk_score": round(float(record["boundary_risk_score"]), 4),
                    "band_reading": "candidate_transition_veto_band",
                }
            )
        return rows

    def _candidate_bundle_rows(self, *, frame: pd.DataFrame) -> list[dict[str, Any]]:
        if frame.empty:
            return []
        offensive = frame.sort_values("forward_return_20d", ascending=False).head(max(10, len(frame) // 8))
        risky = frame.sort_values("penalized_veto_intensity", ascending=False).head(max(10, len(frame) // 8))
        return [
            {
                "bundle_name": "offensive_resonance_direction",
                "feature_1": "ranker_score",
                "feature_2": "catalyst_presence_proxy",
                "feature_3": "core_branch_relative_strength_spread_state",
                "reading": "high-return cluster direction candidate",
                "average_forward_return_20d": round(float(offensive["forward_return_20d"].mean()), 4),
                "average_max_drawdown_20d": round(float(offensive["max_drawdown_20d"].mean()), 4),
            },
            {
                "bundle_name": "veto_resonance_direction",
                "feature_1": "spillover_saturation_overlay_state",
                "feature_2": "internal_turnover_concentration_state",
                "feature_3": "role_deterioration_spread_state",
                "reading": "risk-surface direction candidate",
                "average_penalized_veto_intensity": round(float(risky["penalized_veto_intensity"].mean()), 4),
                "average_max_drawdown_20d": round(float(risky["max_drawdown_20d"].mean()), 4),
            },
        ]


def write_v112bs_penalized_target_mapping_refinement_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BSPenalizedTargetMappingRefinementReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
