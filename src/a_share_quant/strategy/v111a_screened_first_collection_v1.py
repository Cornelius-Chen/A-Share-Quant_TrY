from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V111AScreenedFirstCollectionReport:
    summary: dict[str, Any]
    collection_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "collection_rows": self.collection_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V111AScreenedFirstCollectionAnalyzer:
    """Execute the first bounded acquisition pilot against frozen catalyst rows."""

    ANCHOR_SYMBOL = "300750"

    def analyze(
        self,
        *,
        screened_collection_protocol_payload: dict[str, Any],
        catalyst_source_fill_payload: dict[str, Any],
    ) -> V111AScreenedFirstCollectionReport:
        protocol_summary = dict(screened_collection_protocol_payload.get("summary", {}))
        protocol = dict(screened_collection_protocol_payload.get("protocol", {}))
        if not bool(protocol_summary.get("ready_for_screened_collection_next")):
            raise ValueError("V1.11A protocol must allow screened collection next.")

        candidate_cap = int(protocol.get("candidate_cap", 0))
        admission_cap = int(protocol.get("admission_cap", 0))
        fill_rows = list(catalyst_source_fill_payload.get("fill_rows", []))

        def build_candidate(row: dict[str, Any]) -> dict[str, Any]:
            symbol = str(row.get("symbol", ""))
            persistence_class = str(row.get("persistence_class", ""))
            source_ok = row.get("source_fill_status") == "resolved_official_or_high_trust"
            point_in_time_ok = bool(row.get("event_date")) and bool(row.get("window_start")) and bool(row.get("window_end"))
            confirmation_ok = str(row.get("board_pulse_breadth_class", "")).startswith("mapped_")
            not_single_pulse = persistence_class != "single_pulse"
            novelty_pass = symbol != self.ANCHOR_SYMBOL
            admissible = source_ok and point_in_time_ok and confirmation_ok and not_single_pulse and novelty_pass

            return {
                "lane_id": row.get("lane_id"),
                "symbol": symbol,
                "event_date": row.get("event_date"),
                "event_scope": row.get("event_scope"),
                "event_type": row.get("event_type"),
                "persistence_class": persistence_class,
                "policy_scope": row.get("policy_scope"),
                "source_authority_tier": row.get("source_authority_tier"),
                "primary_source_ref": row.get("primary_source_ref"),
                "mapped_context_name": row.get("mapped_context_name"),
                "novelty_status": "passes_anchor_family_separation" if novelty_pass else "same_anchor_family_reject",
                "admissibility_status": "admit" if admissible else "reject",
                "rejection_reasons": [
                    reason
                    for reason, flag in [
                        ("unresolved_source", not source_ok),
                        ("missing_point_in_time_fields", not point_in_time_ok),
                        ("missing_market_confirmation", not confirmation_ok),
                        ("single_pulse_only", not not_single_pulse),
                        ("same_anchor_family", not novelty_pass),
                    ]
                    if flag
                ],
                "feature_shadow_implication": (
                    "challenge_policy_followthrough_anchor_concentration"
                    if admissible
                    else "no_new_feature_shadow_signal"
                ),
            }

        source_candidates = [
            build_candidate(row)
            for row in fill_rows
            if row.get("source_fill_status") == "resolved_official_or_high_trust"
        ]
        priority_order = {"policy_followthrough": 0, "multi_day_reinforcement": 1}
        sorted_candidates = sorted(
            source_candidates,
            key=lambda row: (
                priority_order.get(str(row.get("persistence_class")), 9),
                str(row.get("symbol")),
                str(row.get("event_date")),
            ),
        )

        screened_rows: list[dict[str, Any]] = []
        admitted_rows: list[dict[str, Any]] = []
        for rank, candidate in enumerate(sorted_candidates[:candidate_cap], start=1):
            screened_row = dict(candidate)
            screened_row["candidate_rank"] = rank
            screened_rows.append(screened_row)
            if candidate.get("admissibility_status") == "admit" and len(admitted_rows) < admission_cap:
                admitted_row = dict(screened_row)
                admitted_row["admission_record_status"] = "admitted_to_bounded_first_pilot"
                admitted_rows.append(admitted_row)

        collection_rows: list[dict[str, Any]] = screened_rows + [
            {
                "lane_id": None,
                "symbol": None,
                "event_date": None,
                "event_scope": None,
                "event_type": None,
                "persistence_class": None,
                "policy_scope": None,
                "source_authority_tier": None,
                "primary_source_ref": None,
                "mapped_context_name": None,
                "novelty_status": None,
                "admissibility_status": "collection_summary",
                "rejection_reasons": [],
                "feature_shadow_implication": None,
                "candidate_rank": None,
                "admission_record_status": (
                    f"screened_{len(screened_rows)}_admitted_{len(admitted_rows)}_under_caps_"
                    f"{candidate_cap}_{admission_cap}"
                ),
            }
        ]

        admitted_policy_followthrough = sum(
            1 for row in admitted_rows if row.get("persistence_class") == "policy_followthrough"
        )
        summary = {
            "acceptance_posture": "open_v111a_screened_first_collection_v1_as_bounded_first_pilot",
            "screened_candidate_count": len(screened_rows),
            "admitted_candidate_count": len(admitted_rows),
            "admitted_new_family_count": len({row.get("symbol") for row in admitted_rows}),
            "admitted_policy_followthrough_count": admitted_policy_followthrough,
            "sample_limit_breaches": 0,
            "ready_for_v111a_phase_check_next": True,
        }
        interpretation = [
            "V1.11A executes the first real acquisition pilot under the frozen infrastructure rather than expanding replay or promotion scope.",
            "The pilot can admit new non-anchor candidates even if they do not yet yield direct policy-followthrough breadth evidence.",
            "The next legal step is a phase check that states clearly whether the pilot produced new candidates, changed the policy-followthrough judgment, or only validated the acquisition path.",
        ]
        return V111AScreenedFirstCollectionReport(
            summary=summary,
            collection_rows=collection_rows,
            interpretation=interpretation,
        )


def write_v111a_screened_first_collection_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V111AScreenedFirstCollectionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
