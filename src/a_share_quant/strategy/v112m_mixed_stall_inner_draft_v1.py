from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from a_share_quant.strategy.v112b_baseline_readout_v1 import TrainingSample
from a_share_quant.strategy.v112g_baseline_readout_v2 import V112GBaselineReadoutV2Analyzer, load_json_report
from a_share_quant.strategy.v112h_candidate_substate_clustering_v1 import V112HCandidateSubstateClusteringAnalyzer


@dataclass(slots=True)
class V112MMixedStallInnerDraftReport:
    summary: dict[str, Any]
    inner_draft_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "inner_draft_rows": self.inner_draft_rows,
            "interpretation": self.interpretation,
        }


class V112MMixedStallInnerDraftAnalyzer:
    FEATURE_NAMES = [
        "theme_breadth_confirmation_proxy",
        "catalyst_freshness_state",
        "cross_day_catalyst_persistence",
        "product_price_change_proxy",
        "relative_strength_persistence",
        "volume_expansion_confirmation",
    ]

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_dataset_payload: dict[str, Any],
        prior_owner_review_payload: dict[str, Any],
    ) -> V112MMixedStallInnerDraftReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_inner_draft_next")):
            raise ValueError("V1.12M requires an open inner-drafting charter.")

        mixed_target_present = any(
            str(row.get("review_disposition")) == "preserve_only_as_inner_drafting_target"
            for row in prior_owner_review_payload.get("review_rows", [])
        )
        if not mixed_target_present:
            raise ValueError("V1.12M requires V1.12L to preserve a mixed stall cluster as an inner-drafting target.")

        samples = V112GBaselineReadoutV2Analyzer().build_augmented_samples(pilot_dataset_payload=pilot_dataset_payload)
        cluster_analyzer = V112HCandidateSubstateClusteringAnalyzer()
        mixed_rows = [
            sample
            for sample in samples
            if sample.stage == "high_level_consolidation"
            and cluster_analyzer._cluster_name(sample) == "breadth_thin_catalyst_stale"
        ]
        if not mixed_rows:
            raise ValueError("V1.12M requires mixed high-level stall rows from the frozen pilot dataset.")

        grouped = {
            "candidate_quiet_contraction_stall_recoverable": [],
            "candidate_residual_breadth_stall_exhaustion": [],
            "candidate_unresolved_mixed_stall_residue": [],
        }
        for sample in mixed_rows:
            fv = sample.feature_values
            breadth = float(fv["theme_breadth_confirmation_proxy"])
            price_change = float(fv["product_price_change_proxy"])
            rel_strength = float(fv["relative_strength_persistence"])
            vol_ratio = float(fv["volume_expansion_confirmation"])

            if breadth >= 0.333333 and price_change <= 0.0:
                grouped["candidate_residual_breadth_stall_exhaustion"].append(sample)
            elif breadth < 0.333333 and price_change <= 0.0 and rel_strength <= 0.0 and vol_ratio < 1.0:
                grouped["candidate_quiet_contraction_stall_recoverable"].append(sample)
            else:
                grouped["candidate_unresolved_mixed_stall_residue"].append(sample)

        inner_draft_rows: list[dict[str, Any]] = []
        for name in [
            "candidate_quiet_contraction_stall_recoverable",
            "candidate_residual_breadth_stall_exhaustion",
            "candidate_unresolved_mixed_stall_residue",
        ]:
            rows = grouped[name]
            label_distribution = dict(sorted(Counter(sample.label for sample in rows).items()))
            carry_count = int(label_distribution.get("carry_constructive", 0))
            failed_count = int(label_distribution.get("failed", 0))

            if name == "candidate_quiet_contraction_stall_recoverable":
                reading = (
                    "A quiet contraction pocket inside the mixed stall cluster: breadth stays thin, price/relative "
                    "strength are soft, and volume is muted rather than distributive. This is the most recoverable "
                    "inner draft."
                )
                readiness = "review_only_inner_draft_candidate"
            elif name == "candidate_residual_breadth_stall_exhaustion":
                reading = (
                    "A residual-breadth stall pocket: some breadth still lingers, but price is no longer advancing. "
                    "This looks closer to exhaustion than recovery."
                )
                readiness = "review_only_inner_draft_candidate"
            else:
                reading = (
                    "The remaining mixed residue after one bounded inner pass. It is still too heterogeneous to preserve "
                    "as a clean review-only inner draft."
                )
                readiness = "unresolved_after_one_inner_pass"

            inner_draft_rows.append(
                {
                    "inner_candidate_name": name,
                    "sample_count": len(rows),
                    "carry_constructive_count": carry_count,
                    "failed_count": failed_count,
                    "watch_constructive_count": int(label_distribution.get("watch_constructive", 0)),
                    "mean_features": self._mean_features(rows),
                    "drafting_readiness": readiness,
                    "reading": reading,
                    "representative_rows": self._representatives(rows),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112m_mixed_stall_inner_draft_v1",
            "mixed_cluster_sample_count": len(mixed_rows),
            "inner_candidate_count": len(inner_draft_rows),
            "preservable_review_only_inner_candidate_count": sum(
                1 for row in inner_draft_rows if row["drafting_readiness"] == "review_only_inner_draft_candidate"
            ),
            "unresolved_inner_residue_count": sum(
                1 for row in inner_draft_rows if row["drafting_readiness"] == "unresolved_after_one_inner_pass"
            ),
            "formal_label_split_now": False,
            "ready_for_phase_check_next": True,
        }
        interpretation = [
            "One bounded inner-drafting pass is enough to reduce the mixed stall cluster into two review-only inner candidates plus one unresolved residue.",
            "The recoverable quiet-contraction pocket is the only inner draft with a carry-heavy skew.",
            "No formal label split is authorized from this inner draft.",
        ]
        return V112MMixedStallInnerDraftReport(
            summary=summary,
            inner_draft_rows=inner_draft_rows,
            interpretation=interpretation,
        )

    def _mean_features(self, rows: list[TrainingSample]) -> dict[str, float]:
        if not rows:
            return {name: 0.0 for name in self.FEATURE_NAMES}
        return {
            name: round(float(sum(float(row.feature_values[name]) for row in rows) / len(rows)), 6)
            for name in self.FEATURE_NAMES
        }

    def _representatives(self, rows: list[TrainingSample]) -> list[dict[str, Any]]:
        if not rows:
            return []
        matrix = np.array([[float(row.feature_values[name]) for name in self.FEATURE_NAMES] for row in rows], dtype=float)
        center = matrix.mean(axis=0)
        distances = np.linalg.norm(matrix - center, axis=1)
        ordered_indices = list(np.argsort(distances)[: min(3, len(rows))])
        return [
            {
                "trade_date": rows[idx].trade_date,
                "symbol": rows[idx].symbol,
                "true_label": rows[idx].label,
                "distance_to_inner_center": round(float(distances[idx]), 6),
                "theme_breadth_confirmation_proxy": round(float(rows[idx].feature_values["theme_breadth_confirmation_proxy"]), 6),
                "product_price_change_proxy": round(float(rows[idx].feature_values["product_price_change_proxy"]), 6),
                "relative_strength_persistence": round(float(rows[idx].feature_values["relative_strength_persistence"]), 6),
                "volume_expansion_confirmation": round(float(rows[idx].feature_values["volume_expansion_confirmation"]), 6),
            }
            for idx in ordered_indices
        ]


def write_v112m_mixed_stall_inner_draft_report(
    *, reports_dir: Path, report_name: str, result: V112MMixedStallInnerDraftReport
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
