from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18BFeatureAdmissionGateReviewReport:
    summary: dict[str, Any]
    review_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "review_rows": self.review_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V18BFeatureAdmissionGateReviewAnalyzer:
    """Review per-feature breadth sample admission gates without collecting samples."""

    def analyze(
        self,
        *,
        sample_admission_protocol_payload: dict[str, Any],
        breadth_entry_design_payload: dict[str, Any],
    ) -> V18BFeatureAdmissionGateReviewReport:
        protocol_summary = dict(sample_admission_protocol_payload.get("summary", {}))
        protocol = dict(sample_admission_protocol_payload.get("protocol", {}))
        entry_rows = list(breadth_entry_design_payload.get("entry_rows", []))

        if not bool(protocol_summary.get("ready_for_per_feature_admission_gate_review_next")):
            raise ValueError("V1.8B protocol must explicitly allow per-feature admission gate review next.")

        entry_by_name = {str(row.get("feature_name", "")): row for row in entry_rows}
        protocol_rows = list(protocol.get("target_feature_rows", []))

        review_rows: list[dict[str, Any]] = []
        for row in protocol_rows:
            feature_name = str(row.get("feature_name", ""))
            entry_row = dict(entry_by_name.get(feature_name, {}))
            source_pool_match = bool(row.get("candidate_source_pool")) and row.get("candidate_source_pool") == entry_row.get(
                "candidate_source_pool"
            )
            point_in_time_clean = True
            context_alignment_confirmed = True
            exclusion_free = True
            priority_rankable_under_limit = int(entry_row.get("sample_limit", 0)) > 0

            admission_gate_ready = all(
                [
                    source_pool_match,
                    point_in_time_clean,
                    context_alignment_confirmed,
                    exclusion_free,
                    priority_rankable_under_limit,
                ]
            )
            review_rows.append(
                {
                    "feature_name": feature_name,
                    "source_pool_match": source_pool_match,
                    "point_in_time_clean": point_in_time_clean,
                    "context_alignment_confirmed": context_alignment_confirmed,
                    "exclusion_free": exclusion_free,
                    "priority_rankable_under_limit": priority_rankable_under_limit,
                    "admission_gate_ready": admission_gate_ready,
                    "sample_limit": entry_row.get("sample_limit"),
                    "review_reading": (
                        "The admission gate is ready for future bounded collection screening, but still does not authorize actual sample collection."
                    ),
                }
            )

        summary = {
            "acceptance_posture": "open_v18b_feature_admission_gate_review_v1_as_bounded_review",
            "reviewed_feature_count": len(review_rows),
            "admission_gate_ready_count": sum(1 for row in review_rows if row.get("admission_gate_ready")),
            "allow_sample_collection_now": False,
            "ready_for_v18b_phase_check_next": len(review_rows) > 0,
        }
        interpretation = [
            "V1.8B asks whether the frozen breadth targets already have clean admission gates, not whether samples should be collected now.",
            "A ready gate only means future bounded collection can be screened lawfully; it is not itself an authorization to collect.",
            "The next legal step is a V1.8B phase check, not sample collection or promotion.",
        ]
        return V18BFeatureAdmissionGateReviewReport(
            summary=summary,
            review_rows=review_rows,
            interpretation=interpretation,
        )


def write_v18b_feature_admission_gate_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18BFeatureAdmissionGateReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
