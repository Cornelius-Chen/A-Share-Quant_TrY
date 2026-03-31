from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V17PromotionEvidenceProtocolReport:
    summary: dict[str, Any]
    protocol: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "protocol": self.protocol,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V17PromotionEvidenceProtocolAnalyzer:
    """Freeze the bounded protocol for promotion-evidence generation."""

    def analyze(
        self,
        *,
        v17_phase_charter_payload: dict[str, Any],
        v16_feature_stability_review_payload: dict[str, Any],
    ) -> V17PromotionEvidenceProtocolReport:
        charter_summary = dict(v17_phase_charter_payload.get("summary", {}))
        review_rows = list(v16_feature_stability_review_payload.get("review_rows", []))

        if not bool(charter_summary.get("do_open_v17_now")):
            raise ValueError("V1.7 charter must be open before the promotion-evidence protocol can be frozen.")

        continuing_candidates = [
            str(row.get("feature_name", ""))
            for row in review_rows
            if row.get("stability_outcome") == "continue_provisional_candidacy"
        ]
        protocol = {
            "provisional_candidate_feature_names": continuing_candidates,
            "promotion_evidence_axes": [
                "sample_breadth_gap",
                "cross_pocket_or_cross_regime_gap",
                "non_redundancy_stress_gap",
                "safe_consumption_beyond_report_only_gap",
            ],
            "admissible_proof_types": [
                "bounded multi-sample review",
                "bounded cross-pocket consistency check",
                "bounded orthogonality stress review",
                "bounded safe-containment extension review",
            ],
            "forbidden_shortcuts": [
                "retained_feature_promotion",
                "strategy_integration",
                "label_relaxation",
                "wide replay expansion",
                "local_model_opening",
            ],
            "phase_target": "state the minimum new evidence required to change promotion judgment without promoting now",
        }
        summary = {
            "acceptance_posture": "freeze_v17_promotion_evidence_protocol_v1",
            "provisional_candidate_count": len(continuing_candidates),
            "promotion_evidence_axis_count": len(protocol["promotion_evidence_axes"]),
            "allow_retained_promotion_now": False,
            "ready_for_per_feature_promotion_gap_review_next": len(continuing_candidates) > 0,
        }
        interpretation = [
            "V1.7 does not reopen candidacy or stability; it identifies the concrete evidence shortfalls that keep current features below promotion threshold.",
            "The protocol stays review-only and forbids promotion, integration, or wide replay shortcuts.",
            "The next legal action is per-feature promotion-evidence gap review, not retained-feature promotion itself.",
        ]
        return V17PromotionEvidenceProtocolReport(
            summary=summary,
            protocol=protocol,
            interpretation=interpretation,
        )


def write_v17_promotion_evidence_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V17PromotionEvidenceProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
