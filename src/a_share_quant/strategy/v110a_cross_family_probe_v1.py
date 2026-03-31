from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V110ACrossFamilyProbeReport:
    summary: dict[str, Any]
    probe_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "probe_rows": self.probe_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V110ACrossFamilyProbeAnalyzer:
    """Run a single screened cross-family probe against the current bounded pool."""

    def analyze(
        self,
        *,
        probe_protocol_payload: dict[str, Any],
        catalyst_seed_payload: dict[str, Any],
        screened_collection_payload: dict[str, Any],
    ) -> V110ACrossFamilyProbeReport:
        protocol_summary = dict(probe_protocol_payload.get("summary", {}))
        protocol = dict(probe_protocol_payload.get("protocol", {}))
        seed_rows = list(catalyst_seed_payload.get("seed_rows", []))
        collection_rows = list(screened_collection_payload.get("collection_rows", []))

        if not bool(protocol_summary.get("ready_for_single_probe_next")):
            raise ValueError("V1.10A protocol must explicitly allow the single probe next.")

        anchor_symbols = set(str(symbol) for symbol in protocol.get("existing_symbol_family_anchor", []))
        sample_limit = int(protocol.get("sample_limit", 0))

        raw_candidates = [
            dict(row)
            for row in seed_rows
            if row.get("lane_outcome_label") == "carry_row_present"
            and row.get("persistence_class") == "policy_followthrough"
        ]

        existing_lane_ids = {
            str(row.get("lane_id", ""))
            for row in collection_rows
            if str(row.get("feature_name", "")) == "policy_followthrough_support"
            and row.get("admission_status") == "admit"
        }

        probe_rows: list[dict[str, Any]] = []
        admitted_count = 0
        for candidate in raw_candidates:
            symbol = str(candidate.get("symbol", ""))
            lane_id = str(candidate.get("lane_id", ""))
            same_family = symbol in anchor_symbols
            already_used = lane_id in existing_lane_ids
            catalyst_context_identical = same_family and str(candidate.get("event_date", "")) == "2024-11-05"
            non_redundant = not same_family and not catalyst_context_identical and not already_used
            admissible = non_redundant and admitted_count < sample_limit

            if admissible:
                admitted_count += 1

            probe_rows.append(
                {
                    "lane_id": lane_id,
                    "symbol": symbol,
                    "event_date": candidate.get("event_date"),
                    "same_symbol_family_as_anchor": same_family,
                    "already_used_in_v18c": already_used,
                    "catalyst_context_identical_to_anchor": catalyst_context_identical,
                    "non_redundant_under_probe_rules": non_redundant,
                    "probe_admission_status": "admit" if admissible else "reject",
                    "rejection_reason": (
                        "same_symbol_family_anchor_cluster"
                        if same_family
                        else "already_used_or_redundant"
                        if already_used or catalyst_context_identical
                        else None
                    ),
                }
            )

        summary = {
            "acceptance_posture": "open_v110a_cross_family_probe_v1_as_single_probe",
            "candidate_count": len(raw_candidates),
            "admitted_case_count": admitted_count,
            "rejected_case_count": sum(1 for row in probe_rows if row.get("probe_admission_status") == "reject"),
            "non_redundant_case_count": sum(
                1 for row in probe_rows if row.get("non_redundant_under_probe_rules")
            ),
            "successful_negative_probe": admitted_count == 0,
            "ready_for_v110a_phase_check_next": True,
        }
        interpretation = [
            "V1.10A does not widen the pool; it screens only the current bounded policy-followthrough candidates.",
            "A case must be cross-family and non-redundant relative to the 300750-based anchor to count.",
            "If no such case exists, the phase still succeeds as a lawful negative probe rather than forcing new evidence.",
        ]
        return V110ACrossFamilyProbeReport(
            summary=summary,
            probe_rows=probe_rows,
            interpretation=interpretation,
        )


def write_v110a_cross_family_probe_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V110ACrossFamilyProbeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
