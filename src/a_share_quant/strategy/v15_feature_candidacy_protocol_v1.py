from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V15FeatureCandidacyProtocolReport:
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


class V15FeatureCandidacyProtocolAnalyzer:
    """Freeze the bounded admissibility protocol for retained-feature candidacy review."""

    def analyze(
        self,
        *,
        v15_phase_charter_payload: dict[str, Any],
        v14_context_feature_schema_payload: dict[str, Any],
        v14_bounded_discrimination_payload: dict[str, Any],
    ) -> V15FeatureCandidacyProtocolReport:
        charter_summary = dict(v15_phase_charter_payload.get("summary", {}))
        schema_rows = list(v14_context_feature_schema_payload.get("schema_rows", []))
        discrimination_summary = dict(v14_bounded_discrimination_payload.get("summary", {}))

        if not bool(charter_summary.get("do_open_v15_now")):
            raise ValueError("V1.5 charter must be open before the candidacy protocol can be frozen.")

        feature_names = [str(row.get("feature_name", "")) for row in schema_rows]
        protocol = {
            "candidate_feature_names": feature_names,
            "review_axes": [
                "feature_admissibility",
                "evidence_sufficiency",
                "non_redundancy_or_orthogonality",
                "safe_containment",
            ],
            "minimum_admissibility_requirements": [
                "point_in_time_clean_definition",
                "source_contamination_controlled",
                "binding_rule_stable_and_auditable",
                "bounded discrimination already present",
                "not strategy-integrated",
            ],
            "candidacy_outcomes": [
                "retain_as_report_only_reject_candidacy",
                "allow_provisional_candidacy_review",
                "hold_for_more_evidence",
            ],
            "forbidden_actions": [
                "retained_feature_promotion",
                "strategy integration",
                "local_model_opening",
                "refresh or replay expansion to manufacture feature evidence",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v15_feature_candidacy_protocol_v1",
            "candidate_feature_count": len(feature_names),
            "review_axis_count": len(protocol["review_axes"]),
            "bounded_discrimination_present": bool(discrimination_summary.get("stable_discrimination_present")),
            "allow_retained_promotion_now": False,
            "ready_for_feature_admissibility_review_next": len(feature_names) > 0,
        }
        interpretation = [
            "V1.5 reviews whether report-only context features deserve candidacy consideration, not whether they should be promoted now.",
            "The protocol turns the next step into an admissibility exercise across evidence, non-redundancy, and safe containment.",
            "The next legal action is per-feature admissibility review, not promotion or model expansion.",
        ]
        return V15FeatureCandidacyProtocolReport(
            summary=summary,
            protocol=protocol,
            interpretation=interpretation,
        )


def write_v15_feature_candidacy_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V15FeatureCandidacyProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
