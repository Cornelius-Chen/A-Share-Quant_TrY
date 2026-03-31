from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V111AScreenedCollectionProtocolReport:
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


class V111AScreenedCollectionProtocolAnalyzer:
    """Freeze the screened protocol for the first acquisition pilot."""

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        v111_plan_payload: dict[str, Any],
    ) -> V111AScreenedCollectionProtocolReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        plan = dict(v111_plan_payload.get("plan", {}))
        if not bool(charter_summary.get("do_open_v111a_now")):
            raise ValueError("V1.11A must be open before its screened collection protocol can be frozen.")

        bounded_plan = dict(plan.get("bounded_first_pilot_plan", {}))
        protocol = {
            "candidate_source_pool": "resolved_official_or_high_trust_rows_from_catalyst_event_registry_source_fill_v1",
            "candidate_cap": int(bounded_plan.get("pilot_candidate_cap", 5)),
            "admission_cap": int(bounded_plan.get("pilot_admission_cap", 2)),
            "pilot_priority_order": list(bounded_plan.get("pilot_priority_order", [])),
            "screening_requirements": [
                "row must satisfy point_in_time_recordable fields",
                "row must have resolved official or high-trust source status",
                "row must have board-level mapped theme or sector confirmation",
                "row must not be single-pulse only",
                "row must pass family novelty rules against existing anchor family",
            ],
            "admission_requirements": [
                "candidate must be non-anchor-family",
                "candidate must preserve source-aware traceability",
                "candidate must remain report-only and exploration-layer only",
                "candidate must record feature-shadow implications",
            ],
            "negative_result_allowed": True,
            "auto_follow_on_forbidden": True,
        }
        summary = {
            "acceptance_posture": "freeze_v111a_screened_collection_protocol_v1",
            "candidate_cap": protocol["candidate_cap"],
            "admission_cap": protocol["admission_cap"],
            "negative_result_allowed": protocol["negative_result_allowed"],
            "ready_for_screened_collection_next": True,
        }
        interpretation = [
            "V1.11A screens only resolved, source-aware catalyst rows rather than opening a fresh replay branch.",
            "The pilot is deliberately small: it can screen at most five candidates and admit at most two.",
            "The next legal step is to execute the screen and record admissions or a clean negative result.",
        ]
        return V111AScreenedCollectionProtocolReport(summary=summary, protocol=protocol, interpretation=interpretation)


def write_v111a_screened_collection_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V111AScreenedCollectionProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
