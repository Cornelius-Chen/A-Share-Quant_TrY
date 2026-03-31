from __future__ import annotations

import json
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import numpy as np
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score


@dataclass(slots=True)
class V112ACUnsupervisedRoleChallengeProbeReport:
    summary: dict[str, Any]
    feature_axes: dict[str, list[str]]
    cluster_rows: list[dict[str, Any]]
    challenge_rows: list[dict[str, Any]]
    candidate_structure_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "feature_axes": self.feature_axes,
            "cluster_rows": self.cluster_rows,
            "challenge_rows": self.challenge_rows,
            "candidate_structure_rows": self.candidate_structure_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _broad_manual_bucket(cohort_layer: str) -> str:
    if cohort_layer in {"core_anchor", "core_beta", "core_platform_confirmation"}:
        return "core"
    if cohort_layer in {"adjacent_bridge", "adjacent_high_beta_extension"}:
        return "adjacent"
    if cohort_layer in {"branch_extension", "late_extension"}:
        return "branch_or_late"
    if cohort_layer in {"spillover_candidate", "weak_memory"}:
        return "spillover_or_memory"
    return "pending"


def _top_items(counter: Counter[str], limit: int = 5) -> list[str]:
    return [item for item, _ in counter.most_common(limit)]


class V112ACUnsupervisedRoleChallengeProbeAnalyzer:
    CLUSTER_COUNT = 4

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        cohort_map_payload: dict[str, Any],
        labeling_review_payload: dict[str, Any],
    ) -> V112ACUnsupervisedRoleChallengeProbeReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("do_open_v112ac_now")):
            raise ValueError("V1.12AC must be open before the unsupervised role-challenge probe runs.")

        cohort_rows = list(cohort_map_payload.get("object_role_time_rows", []))
        label_rows = list(labeling_review_payload.get("labeling_surface_rows", []))
        if not cohort_rows or not label_rows:
            raise ValueError("V1.12AC requires the bounded cohort map and bounded labeling review outputs.")

        symbol_to_surface = {
            str(row.get("symbol")): str(row.get("labeling_surface"))
            for row in label_rows
        }
        stage_names = sorted({stage for row in cohort_rows for stage in list(row.get("active_stage_windows", []))})
        evidence_axes = sorted({axis for row in cohort_rows for axis in list(row.get("evidence_axes", []))})

        matrix_rows: list[np.ndarray] = []
        row_metadata: list[dict[str, Any]] = []
        for row in cohort_rows:
            symbol = str(row.get("symbol"))
            active_stages = set(str(stage) for stage in row.get("active_stage_windows", []))
            active_axes = set(str(axis) for axis in row.get("evidence_axes", []))
            stage_vector = [1.0 if stage in active_stages else 0.0 for stage in stage_names]
            axis_vector = [1.0 if axis in active_axes else 0.0 for axis in evidence_axes]
            vector = np.array(stage_vector + axis_vector, dtype=float)
            matrix_rows.append(vector)
            row_metadata.append(
                {
                    "symbol": symbol,
                    "cohort_layer": str(row.get("cohort_layer")),
                    "manual_bucket": _broad_manual_bucket(str(row.get("cohort_layer"))),
                    "role_family": str(row.get("role_family")),
                    "labeling_surface": symbol_to_surface.get(symbol, "unknown_surface"),
                    "active_stage_windows": list(row.get("active_stage_windows", [])),
                    "evidence_axes": list(row.get("evidence_axes", [])),
                }
            )

        x = np.vstack(matrix_rows)
        kmeans = KMeans(n_clusters=self.CLUSTER_COUNT, n_init=20, random_state=42)
        kmeans_labels = kmeans.fit_predict(x)
        agglomerative = AgglomerativeClustering(n_clusters=self.CLUSTER_COUNT)
        agglomerative_labels = agglomerative.fit_predict(x)

        preferred_labels = agglomerative_labels
        cluster_rows: list[dict[str, Any]] = []
        challenge_rows: list[dict[str, Any]] = []
        candidate_structure_rows: list[dict[str, Any]] = []

        supportive_cluster_count = 0
        challenging_cluster_count = 0
        spillover_separation_supported = False
        pending_quiet_window_supported = False

        for cluster_id in range(self.CLUSTER_COUNT):
            member_indexes = [idx for idx, label in enumerate(preferred_labels) if int(label) == cluster_id]
            members = [row_metadata[idx] for idx in member_indexes]
            bucket_counter = Counter(member["manual_bucket"] for member in members)
            surface_counter = Counter(member["labeling_surface"] for member in members)
            stage_counter = Counter(stage for member in members for stage in member["active_stage_windows"])
            axis_counter = Counter(axis for member in members for axis in member["evidence_axes"])
            dominant_bucket, dominant_bucket_count = bucket_counter.most_common(1)[0]
            dominant_share = dominant_bucket_count / len(members)
            posture = "supportive_cluster" if dominant_share >= 0.6 else "challenging_mixed_cluster"
            if posture == "supportive_cluster":
                supportive_cluster_count += 1
            else:
                challenging_cluster_count += 1

            top_stages = _top_items(stage_counter, limit=4)
            top_axes = _top_items(axis_counter, limit=5)
            if dominant_bucket == "spillover_or_memory" and dominant_share >= 0.6:
                spillover_separation_supported = True
            if dominant_bucket == "pending" and any(stage == "deep_reset_quiet_window" for stage in top_stages):
                pending_quiet_window_supported = True

            if dominant_bucket == "core":
                candidate_reading = "candidate_core_markup_strength_signature"
            elif dominant_bucket == "branch_or_late" and any("re_ignition" in stage or "major_markup" in stage for stage in top_stages):
                candidate_reading = "candidate_branch_or_route_depth_signature"
            elif dominant_bucket == "spillover_or_memory":
                candidate_reading = "candidate_late_cycle_maturity_spillover_signature"
            elif dominant_bucket == "pending":
                candidate_reading = "candidate_quiet_window_pending_signature"
            else:
                candidate_reading = "candidate_diffusion_extension_signature"

            cluster_rows.append(
                {
                    "cluster_id": cluster_id,
                    "posture": posture,
                    "member_symbols": [member["symbol"] for member in members],
                    "manual_bucket_mix": dict(bucket_counter),
                    "labeling_surface_mix": dict(surface_counter),
                    "top_stage_windows": top_stages,
                    "top_evidence_axes": top_axes,
                    "candidate_reading": candidate_reading,
                    "reading": self._cluster_reading(
                        dominant_bucket=dominant_bucket,
                        dominant_share=dominant_share,
                        top_stages=top_stages,
                    ),
                }
            )

            if posture == "challenging_mixed_cluster":
                challenge_rows.append(
                    {
                        "challenge_name": f"cluster_{cluster_id}_mixed_boundary",
                        "member_symbols": [member["symbol"] for member in members],
                        "why_it_matters": (
                            "The data-side structure does not cleanly respect the current manual boundary here, "
                            "so later label drafting should treat this region as review-first."
                        ),
                        "manual_bucket_mix": dict(bucket_counter),
                        "top_stage_windows": top_stages,
                    }
                )

            candidate_structure_rows.append(
                {
                    "candidate_structure_name": candidate_reading,
                    "source_cluster_id": cluster_id,
                    "status": "review_only_candidate_structure",
                    "member_symbols": [member["symbol"] for member in members],
                    "top_stage_windows": top_stages,
                    "top_evidence_axes": top_axes,
                    "do_not_treat_as": "formal_label_or_formal_role",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112ac_unsupervised_role_challenge_probe_v1",
            "row_count": len(cohort_rows),
            "feature_dimension_count": int(x.shape[1]),
            "stage_feature_count": len(stage_names),
            "evidence_axis_feature_count": len(evidence_axes),
            "preferred_clustering_family": "agglomerative_clustering",
            "cluster_count": self.CLUSTER_COUNT,
            "kmeans_agglomerative_ari": round(float(adjusted_rand_score(kmeans_labels, agglomerative_labels)), 4),
            "supportive_cluster_count": supportive_cluster_count,
            "challenging_cluster_count": challenging_cluster_count,
            "spillover_separation_supported": spillover_separation_supported,
            "pending_quiet_window_supported": pending_quiet_window_supported,
            "formal_role_replacement_forbidden": True,
            "formal_label_freeze_still_forbidden": True,
            "formal_training_still_forbidden": True,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "The unsupervised probe is a challenger, not a legislator.",
            "Current manual roles are partly supported by data-side latent structure, but some adjacent/branch boundaries remain mixed.",
            "Any new latent signatures remain review-only candidate structures until later owner review says otherwise.",
        ]
        return V112ACUnsupervisedRoleChallengeProbeReport(
            summary=summary,
            feature_axes={
                "stage_windows": stage_names,
                "evidence_axes": evidence_axes,
            },
            cluster_rows=cluster_rows,
            challenge_rows=challenge_rows,
            candidate_structure_rows=candidate_structure_rows,
            interpretation=interpretation,
        )

    def _cluster_reading(self, *, dominant_bucket: str, dominant_share: float, top_stages: list[str]) -> str:
        if dominant_bucket == "core":
            return "Data-side structure still recognizes a relatively coherent core group centered on markup-bearing rows."
        if dominant_bucket == "spillover_or_memory":
            return "Data-side structure recognizes a late-cycle spillover or weak-memory surface separate from core truth."
        if dominant_bucket == "pending":
            return "Data-side structure keeps a quiet-window pending pocket that should not be force-labeled."
        if dominant_bucket == "branch_or_late" and any("laggard" in stage for stage in top_stages):
            return "Branch and late extension rows can cluster around cycle-maturity rather than core-business purity."
        if dominant_share < 0.6:
            return "This mixed cluster challenges the cleanliness of the current manual boundary and should remain review-first."
        return "The cluster is partially supportive, but still bounded and review-only."


def write_v112ac_unsupervised_role_challenge_probe_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112ACUnsupervisedRoleChallengeProbeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
