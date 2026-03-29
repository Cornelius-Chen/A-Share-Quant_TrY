from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class U2PocketClusteringReadinessReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class U2PocketClusteringReadinessAnalyzer:
    """Decide whether the bounded U2 clustering step should start."""

    def analyze(
        self,
        *,
        feature_gap_payload: dict[str, Any],
        feature_pack_c_acceptance_payload: dict[str, Any],
        u1_payload: dict[str, Any],
    ) -> U2PocketClusteringReadinessReport:
        gap_summary = dict(feature_gap_payload.get("summary", {}))
        acceptance_summary = dict(feature_pack_c_acceptance_payload.get("summary", {}))
        u1_summary = dict(u1_payload.get("summary", {}))

        suspect_count = int(gap_summary.get("feature_gap_suspect_count", 0))
        thinning_signal = bool(gap_summary.get("thinning_signal"))
        pack_c_closed = (
            str(acceptance_summary.get("acceptance_posture"))
            == "close_feature_pack_c_as_explanatory_and_prepare_u1_sidecar"
        )
        centroid_distance = float(u1_summary.get("case_centroid_distance", 0.0) or 0.0)
        geometrically_separable = str(u1_summary.get("separation_reading")) == "cases_geometrically_separable"

        ready = suspect_count >= 4 and not geometrically_separable and pack_c_closed
        recommended_next_phase = (
            "u2_pocket_clustering"
            if ready
            else "hold_u2_and_wait_for_larger_or_less_separable_suspect_set"
        )
        summary = {
            "suspect_count": suspect_count,
            "thinning_signal": thinning_signal,
            "feature_pack_c_closed": pack_c_closed,
            "u1_case_centroid_distance": round(centroid_distance, 6),
            "u1_cases_geometrically_separable": geometrically_separable,
            "u2_ready": ready,
            "recommended_next_phase": recommended_next_phase,
        }
        evidence_rows = [
            {
                "evidence_name": "suspect_set_size",
                "actual": {
                    "feature_gap_suspect_count": suspect_count,
                    "minimum_for_u2": 4,
                },
                "reading": "Pocket clustering is only worthwhile if the suspect set is large enough to form more than a trivial split.",
            },
            {
                "evidence_name": "pack_c_exit",
                "actual": {
                    "acceptance_posture": acceptance_summary.get("acceptance_posture"),
                    "ready_for_u1_lightweight_geometry": acceptance_summary.get("ready_for_u1_lightweight_geometry"),
                },
                "reading": "Pack-C has already closed as explanatory, so the next sidecar decision should be based on evidence quality rather than on unfinished pack work.",
            },
            {
                "evidence_name": "u1_geometry",
                "actual": {
                    "case_centroid_distance": round(centroid_distance, 6),
                    "separation_reading": u1_summary.get("separation_reading"),
                },
                "reading": "If the current suspects are already cleanly separable, clustering adds less value than simply treating them as different lanes.",
            },
        ]
        interpretation = [
            "U2 clustering should begin only when there are enough unresolved suspects and the current pockets are still blended enough that clustering can change the next feature-pack decision.",
            "The current state fails that bar because the suspect set is small and U1 already separated the two active pockets cleanly.",
            "So the right action is to hold U2, not to force a clustering phase for its own sake.",
        ]
        return U2PocketClusteringReadinessReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_u2_pocket_clustering_readiness_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: U2PocketClusteringReadinessReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
