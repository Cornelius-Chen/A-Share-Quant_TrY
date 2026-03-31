from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18ASampleBreadthProtocolReport:
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


class V18ASampleBreadthProtocolAnalyzer:
    """Freeze the bounded protocol for sample-breadth expansion."""

    def analyze(
        self,
        *,
        v18a_phase_charter_payload: dict[str, Any],
        v17_feature_promotion_gap_review_payload: dict[str, Any],
    ) -> V18ASampleBreadthProtocolReport:
        charter_summary = dict(v18a_phase_charter_payload.get("summary", {}))
        review_rows = list(v17_feature_promotion_gap_review_payload.get("review_rows", []))

        if not bool(charter_summary.get("do_open_v18a_now")):
            raise ValueError("V1.8A charter must be open before the sample-breadth protocol can be frozen.")

        target_names = set(str(name) for name in charter_summary.get("target_feature_names", []))
        protocol_rows = []
        for row in review_rows:
            feature_name = str(row.get("feature_name", ""))
            if feature_name not in target_names:
                continue
            protocol_rows.append(
                {
                    "feature_name": feature_name,
                    "primary_shortfall": row.get("primary_shortfall"),
                    "minimum_evidence_path": row.get("minimum_evidence_path"),
                    "breadth_target_type": "bounded_additional_cases",
                }
            )

        protocol = {
            "target_feature_rows": protocol_rows,
            "bounded_entry_rules": [
                "new samples must be tied to explicit sample_breadth shortfall only",
                "new samples must not widen into generic replay growth",
                "new samples must preserve point_in_time and source_aware constraints",
                "new samples must stay below promotion and strategy integration thresholds",
            ],
            "allowed_evidence_sample_types": [
                "bounded additional opening-like cases for single_pulse_support",
                "bounded additional followthrough-like cases for policy_followthrough_support",
            ],
            "forbidden_actions": [
                "retained_feature_promotion",
                "strategy_integration",
                "mixed shortfall expansion",
                "wide replay queue reopening",
                "local_model_opening",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v18a_sample_breadth_protocol_v1",
            "target_feature_count": len(protocol_rows),
            "allowed_evidence_sample_type_count": len(protocol["allowed_evidence_sample_types"]),
            "allow_retained_promotion_now": False,
            "ready_for_breadth_entry_design_next": len(protocol_rows) > 0,
        }
        interpretation = [
            "V1.8A does not collect arbitrary new samples; it targets only the features whose primary shortfall is sample breadth.",
            "The protocol keeps breadth expansion bounded, source-aware, and below any promotion or strategy-integration threshold.",
            "The next legal action is breadth-entry design, not generic replay or direct promotion.",
        ]
        return V18ASampleBreadthProtocolReport(
            summary=summary,
            protocol=protocol,
            interpretation=interpretation,
        )


def write_v18a_sample_breadth_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18ASampleBreadthProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
