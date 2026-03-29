from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FeaturePackBHierarchyApprovalReport:
    summary: dict[str, Any]
    case_row: dict[str, Any]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "case_row": self.case_row,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class FeaturePackBHierarchyApprovalAnalyzer:
    """Focus track A on the clean hierarchy / approval suspect before broader feature work resumes."""

    def analyze(self, *, recheck_report_path: Path, case_name: str) -> FeaturePackBHierarchyApprovalReport:
        payload = load_json_report(recheck_report_path)
        rows = [row for row in payload.get("case_rows", []) if str(row["case_name"]) == case_name]
        if not rows:
            raise ValueError(f"Case {case_name} not found in {recheck_report_path}")

        late_quality_straddles = sum(bool(row.get("late_quality_straddle")) for row in rows)
        non_junk_straddles = sum(bool(row.get("non_junk_straddle")) for row in rows)
        margin_straddles = sum(bool(row.get("margin_straddle")) for row in rows)
        permission_split_rows = sum(
            row.get("incumbent_permission_allowed") != row.get("challenger_permission_allowed")
            for row in rows
        )
        fallback_rows = sum(
            str(row.get("challenger_assignment_reason")) in {"fallback_to_junk", "low_composite_or_low_resonance"}
            for row in rows
        )
        avg_fallback_reason_score = round(
            sum(float(row.get("fallback_reason_score", 0.0)) for row in rows) / len(rows),
            6,
        )
        avg_challenger_margin_gap = round(
            sum(float(row.get("challenger_margin_gap", 0.0)) for row in rows) / len(rows),
            6,
        )
        avg_challenger_late_margin = round(
            sum(float(row.get("challenger_late_quality_margin", 0.0)) for row in rows) / len(rows),
            6,
        )

        if margin_straddles >= permission_split_rows and margin_straddles > 0:
            dominant_approval_edge = "score_margin_threshold"
        elif permission_split_rows > 0:
            dominant_approval_edge = "permission_state_divergence"
        else:
            dominant_approval_edge = "hierarchy_only"

        dominant_hierarchy_edge = "late_mover_quality"
        if non_junk_straddles > late_quality_straddles:
            dominant_hierarchy_edge = "non_junk_composite"

        summary = {
            "case_name": case_name,
            "row_count": len(rows),
            "dominant_hierarchy_edge": dominant_hierarchy_edge,
            "dominant_approval_edge": dominant_approval_edge,
            "late_quality_straddles": late_quality_straddles,
            "non_junk_straddles": non_junk_straddles,
            "margin_straddles": margin_straddles,
            "permission_split_rows": permission_split_rows,
            "fallback_rows": fallback_rows,
            "avg_fallback_reason_score": avg_fallback_reason_score,
            "avg_challenger_margin_gap": avg_challenger_margin_gap,
            "avg_challenger_late_quality_margin": avg_challenger_late_margin,
            "recommended_focus": [
                "fallback_reason_score",
                "late_mover_quality_margin",
                "min_score_margin",
                "approval_hysteresis_state",
                "switch_buffer_pressure",
            ],
        }
        interpretation = [
            "If margin straddles explain the permission split, the next refinement should target approval thresholds before adding more concept features.",
            "If late-quality straddles dominate at the same time, the pocket is best treated as a coupled hierarchy-plus-approval edge.",
            "This track should finish before the concept-supported hierarchy track is opened.",
        ]
        return FeaturePackBHierarchyApprovalReport(
            summary=summary,
            case_row={"case_name": case_name, "rows": rows},
            interpretation=interpretation,
        )


def write_feature_pack_b_hierarchy_approval_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackBHierarchyApprovalReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
