from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18BSampleAdmissionProtocolReport:
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


class V18BSampleAdmissionProtocolAnalyzer:
    """Freeze the bounded protocol for breadth sample admission gating."""

    def analyze(
        self,
        *,
        v18b_phase_charter_payload: dict[str, Any],
        v18a_breadth_entry_design_payload: dict[str, Any],
    ) -> V18BSampleAdmissionProtocolReport:
        charter_summary = dict(v18b_phase_charter_payload.get("summary", {}))
        entry_rows = list(v18a_breadth_entry_design_payload.get("entry_rows", []))

        if not bool(charter_summary.get("do_open_v18b_now")):
            raise ValueError("V1.8B charter must be open before the sample admission protocol can be frozen.")

        target_names = set(str(name) for name in charter_summary.get("target_feature_names", []))
        protocol_rows: list[dict[str, Any]] = []
        for row in entry_rows:
            feature_name = str(row.get("feature_name", ""))
            if feature_name not in target_names:
                continue
            protocol_rows.append(
                {
                    "feature_name": feature_name,
                    "candidate_source_pool": row.get("candidate_source_pool"),
                    "sample_limit": row.get("sample_limit"),
                    "admission_axes": [
                        "source_pool_match",
                        "point_in_time_clean",
                        "context_alignment_confirmed",
                        "exclusion_free",
                        "priority_rankable_under_limit",
                    ],
                    "mandatory_exclusions": [
                        "ambiguous_context_alignment",
                        "source_or_market_confirmation_break",
                        "mixed_shortfall_candidate",
                        "queue_widening_only_case",
                    ],
                }
            )

        protocol = {
            "target_feature_rows": protocol_rows,
            "global_gate_rules": [
                "candidates must remain inside the frozen breadth-entry source pool",
                "candidates must preserve point_in_time and source-aware constraints",
                "candidates must preserve the target feature reading without relabeling",
                "admission does not authorize collection beyond current sample limits",
            ],
            "forbidden_actions": [
                "sample_collection",
                "retained_feature_promotion",
                "strategy_integration",
                "generic_replay_growth",
                "mixed_shortfall_expansion",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v18b_sample_admission_protocol_v1",
            "target_feature_count": len(protocol_rows),
            "allow_sample_collection_now": False,
            "ready_for_per_feature_admission_gate_review_next": len(protocol_rows) > 0,
        }
        interpretation = [
            "V1.8B does not admit actual samples yet; it freezes the gate that future candidates must pass.",
            "The protocol keeps admission bounded to the two breadth targets and preserves all point-in-time and source-aware guardrails.",
            "The next legal action is per-feature admission gate review, not collection or promotion.",
        ]
        return V18BSampleAdmissionProtocolReport(
            summary=summary,
            protocol=protocol,
            interpretation=interpretation,
        )


def write_v18b_sample_admission_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18BSampleAdmissionProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
