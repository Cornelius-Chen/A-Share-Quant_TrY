from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FeaturePackCReadinessReport:
    summary: dict[str, Any]
    track_rows: list[dict[str, Any]]
    recommended_features: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "track_rows": self.track_rows,
            "recommended_features": self.recommended_features,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class FeaturePackCReadinessAnalyzer:
    """Summarize why feature-pack-b ended and what feature-pack-c should target."""

    def analyze(
        self,
        *,
        feature_gap_payload: dict[str, Any],
        track_a_payload: dict[str, Any],
        track_a_sweep_payload: dict[str, Any],
        track_b_payload: dict[str, Any],
        track_b_validation_payload: dict[str, Any],
    ) -> FeaturePackCReadinessReport:
        feature_gap_summary = dict(feature_gap_payload.get("summary", {}))
        track_a_summary = dict(track_a_payload.get("summary", {}))
        track_a_best = dict(track_a_sweep_payload.get("candidate_rows", [{}])[0])
        track_b_summary = dict(track_b_payload.get("summary", {}))
        track_b_validation_summary = dict(track_b_validation_payload.get("summary", {}))

        track_rows = [
            {
                "track_name": "track_a_hierarchy_approval",
                "case_name": track_a_summary.get("case_name"),
                "status": "closed_negative_informative",
                "dominant_edge": {
                    "hierarchy": track_a_summary.get("dominant_hierarchy_edge"),
                    "approval": track_a_summary.get("dominant_approval_edge"),
                },
                "repair_result": {
                    "best_local_repair_candidate": track_a_best.get("candidate_name"),
                    "best_local_repair_profile": track_a_best.get("repair_profile"),
                    "best_local_repair_total_pnl": track_a_best.get("total_pnl"),
                },
                "reading": "Hierarchy and approval edges are real, but local repairs degraded or failed to improve the pocket economics.",
            },
            {
                "track_name": "track_b_concept_to_late",
                "case_name": track_b_summary.get("case_name"),
                "status": str(track_b_validation_summary.get("acceptance_posture")),
                "dominant_edge": {
                    "bridge": track_b_summary.get("dominant_bridge"),
                    "late_quality_straddles": track_b_summary.get("late_quality_straddles"),
                    "concept_supported_late_rows": track_b_summary.get("concept_supported_late_rows"),
                },
                "repair_result": {
                    "best_variant_name": track_b_validation_summary.get("best_variant_name"),
                    "best_variant_alpha_retention_ratio": track_b_validation_summary.get("best_variant_alpha_retention_ratio"),
                    "best_variant_repair_completion_ratio": track_b_validation_summary.get("best_variant_repair_completion_ratio"),
                },
                "reading": "Concept-aware late-mover variants repaired one trigger row but retained too little alpha to justify continued widening.",
            },
        ]

        recommended_features = [
            {
                "feature_name": "fallback_reason_decomposition",
                "priority": 1,
                "why_now": "Both tracks terminate at junk/fallback boundaries, but the current fallback score is too compressed to distinguish cheap repairs from structural failures.",
                "target_pockets": ["theme_q4 / 002902 / B", "theme_q2 / 002466 / C"],
            },
            {
                "feature_name": "late_quality_residual_components",
                "priority": 2,
                "why_now": "Late-mover admission is the recurring bottleneck across both tracks, but only the scalar margin is visible today.",
                "target_pockets": ["theme_q4 / 002902 / B", "theme_q2 / 002466 / C"],
            },
            {
                "feature_name": "approval_threshold_history",
                "priority": 3,
                "why_now": "Approval edges appear near thresholds and may depend on short hysteresis sequences rather than same-day gaps alone.",
                "target_pockets": ["theme_q4 / 002902 / B"],
            },
            {
                "feature_name": "concept_support_excess_to_late_threshold",
                "priority": 4,
                "why_now": "Track B suggests that raw concept support is insufficient; what matters is support relative to the late-mover admission deficit.",
                "target_pockets": ["theme_q2 / 002466 / C"],
            },
        ]

        summary = {
            "feature_gap_suspect_count": feature_gap_summary.get("feature_gap_suspect_count"),
            "thinning_signal": bool(feature_gap_summary.get("thinning_signal")),
            "track_a_closed": True,
            "track_b_closed": track_b_validation_summary.get("acceptance_posture")
            == "close_track_b_as_negative_informative",
            "recommended_next_phase": "feature_pack_c_local_causal_edges",
            "do_restart_replay_queue": False,
            "recommended_track_count": len(track_rows),
            "recommended_feature_count": len(recommended_features),
        }
        interpretation = [
            "Feature-pack-c should begin only after both feature-pack-b tracks are treated as closed, so the next pack does not inherit the old local-parameter loop.",
            "The next features should be causal and local, not broader thresholds: the current evidence says we are under-observing why pockets fall into junk or miss late-mover admission.",
            "Replay queue expansion should remain paused until at least one feature-pack-c recheck changes a pocket boundary more cleanly than the current feature-pack-b variants did.",
        ]
        return FeaturePackCReadinessReport(
            summary=summary,
            track_rows=track_rows,
            recommended_features=recommended_features,
            interpretation=interpretation,
        )


def write_feature_pack_c_readiness_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackCReadinessReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
