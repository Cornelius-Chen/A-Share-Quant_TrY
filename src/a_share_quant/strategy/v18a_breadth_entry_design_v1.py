from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18ABreadthEntryDesignReport:
    summary: dict[str, Any]
    entry_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "entry_rows": self.entry_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V18ABreadthEntryDesignAnalyzer:
    """Define the minimum lawful evidence-sample entry for V1.8A sample-breadth expansion."""

    def analyze(
        self,
        *,
        sample_breadth_protocol_payload: dict[str, Any],
    ) -> V18ABreadthEntryDesignReport:
        protocol_summary = dict(sample_breadth_protocol_payload.get("summary", {}))
        protocol = dict(sample_breadth_protocol_payload.get("protocol", {}))

        if not bool(protocol_summary.get("ready_for_breadth_entry_design_next")):
            raise ValueError("V1.8A protocol must explicitly allow breadth-entry design next.")

        target_rows = list(protocol.get("target_feature_rows", []))
        entry_rows: list[dict[str, Any]] = []
        for row in target_rows:
            feature_name = str(row.get("feature_name", ""))
            if feature_name == "single_pulse_support":
                entry_rows.append(
                    {
                        "feature_name": feature_name,
                        "breadth_entry_mode": "bounded_additional_opening_cases",
                        "candidate_source_pool": "closed_opening_led_lanes_with_context_rows",
                        "sample_limit": 3,
                        "selection_rules": [
                            "must remain point_in_time clean",
                            "must remain source_aware and market_confirmed",
                            "must not reopen generic replay queues",
                            "must not mix in persistence_or_carry shortfall targets",
                        ],
                        "minimum_evidence_path": row.get("minimum_evidence_path"),
                    }
                )
            elif feature_name == "policy_followthrough_support":
                entry_rows.append(
                    {
                        "feature_name": feature_name,
                        "breadth_entry_mode": "bounded_additional_followthrough_cases",
                        "candidate_source_pool": "closed_followthrough_like_lanes_with_policy_or_industry_context",
                        "sample_limit": 3,
                        "selection_rules": [
                            "must preserve policy_or_industry_followthrough reading",
                            "must remain point_in_time clean and source_aware",
                            "must avoid generic catalyst ingestion growth",
                            "must not mix in cross_regime validation work",
                        ],
                        "minimum_evidence_path": row.get("minimum_evidence_path"),
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v18a_breadth_entry_design_v1",
            "entry_row_count": len(entry_rows),
            "target_feature_count": len(target_rows),
            "allow_unbounded_sample_collection_now": False,
            "ready_for_v18a_phase_check_next": len(entry_rows) > 0,
        }
        interpretation = [
            "V1.8A still does not collect arbitrary new samples; it only defines the smallest lawful entry design for future breadth evidence work.",
            "The entry design remains tied to two explicit target features and keeps source-aware, point-in-time, and boundedness constraints intact.",
            "The next legal step is a V1.8A phase check, not generic sample collection or promotion.",
        ]
        return V18ABreadthEntryDesignReport(
            summary=summary,
            entry_rows=entry_rows,
            interpretation=interpretation,
        )


def write_v18a_breadth_entry_design_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18ABreadthEntryDesignReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
