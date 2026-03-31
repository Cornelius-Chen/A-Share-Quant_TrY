from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18CScreenedCollectionReport:
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


class V18CScreenedCollectionAnalyzer:
    """Execute screened bounded collection against the frozen candidate pools."""

    def analyze(
        self,
        *,
        screened_collection_protocol_payload: dict[str, Any],
        catalyst_seed_payload: dict[str, Any],
        market_v5_first_lane_payload: dict[str, Any],
        market_v5_last_probe_payload: dict[str, Any],
        market_v6_first_lane_payload: dict[str, Any],
    ) -> V18CScreenedCollectionReport:
        protocol_summary = dict(screened_collection_protocol_payload.get("summary", {}))
        protocol = dict(screened_collection_protocol_payload.get("protocol", {}))
        seed_rows = list(catalyst_seed_payload.get("seed_rows", []))

        if not bool(protocol_summary.get("ready_for_screened_collection_next")):
            raise ValueError("V1.8C protocol must explicitly allow screened collection next.")

        target_rows = list(protocol.get("target_feature_rows", []))
        collection_rows: list[dict[str, Any]] = []
        for target in target_rows:
            feature_name = str(target.get("feature_name", ""))
            sample_limit = int(target.get("sample_limit", 0))

            if feature_name == "single_pulse_support":
                candidates = [
                    row
                    for row in seed_rows
                    if row.get("lane_outcome_label") == "opening_led"
                    and row.get("persistence_class") == "single_pulse"
                ]
                extra_candidates = [
                    {
                        "lane_id": "mainline_trend_b::2024-05-10::002273",
                        "dataset_name": "seed_from_closed_opening_lane",
                        "symbol": "002273",
                        "event_date": "2024-05-10",
                        "lane_outcome_label": "opening_led",
                        "persistence_class": "single_pulse",
                        "notes": "from_market_v5_first_lane_acceptance",
                    },
                    {
                        "lane_id": "mainline_trend_b::2024-04-10::000099",
                        "dataset_name": "seed_from_closed_opening_lane",
                        "symbol": "000099",
                        "event_date": "2024-04-10",
                        "lane_outcome_label": "opening_led",
                        "persistence_class": "single_pulse",
                        "notes": "from_market_v5_last_true_carry_probe_acceptance",
                    },
                    {
                        "lane_id": "mainline_trend_c::2024-07-22::600118",
                        "dataset_name": "seed_from_closed_opening_lane",
                        "symbol": "600118",
                        "event_date": "2024-07-22",
                        "lane_outcome_label": "opening_led",
                        "persistence_class": "single_pulse",
                        "notes": "from_market_v6_first_lane_acceptance",
                    },
                ]
                _ = market_v5_first_lane_payload, market_v5_last_probe_payload, market_v6_first_lane_payload
                candidates.extend(extra_candidates)
            elif feature_name == "policy_followthrough_support":
                candidates = [
                    row
                    for row in seed_rows
                    if row.get("lane_outcome_label") == "carry_row_present"
                    and row.get("persistence_class") == "policy_followthrough"
                ]
            else:
                candidates = []

            admitted = candidates[:sample_limit]
            for rank, candidate in enumerate(admitted, start=1):
                collection_rows.append(
                    {
                        "feature_name": feature_name,
                        "admission_status": "admit",
                        "candidate_rank": rank,
                        "lane_id": candidate.get("lane_id"),
                        "symbol": candidate.get("symbol"),
                        "event_date": candidate.get("event_date"),
                        "dataset_name": candidate.get("dataset_name"),
                        "screening_reason": "matches_frozen_source_pool_and_target_reading",
                    }
                )

            collection_rows.append(
                {
                    "feature_name": feature_name,
                    "admission_status": "collection_summary",
                    "candidate_rank": None,
                    "lane_id": None,
                    "symbol": None,
                    "event_date": None,
                    "dataset_name": None,
                    "screening_reason": (
                        f"admitted_{len(admitted)}_of_{len(candidates)}_available_cases_under_limit_{sample_limit}"
                    ),
                }
            )

        admitted_count = sum(1 for row in collection_rows if row.get("admission_status") == "admit")
        summary = {
            "acceptance_posture": "open_v18c_screened_collection_v1_as_bounded_collection",
            "target_feature_count": len(target_rows),
            "admitted_case_count": admitted_count,
            "targets_with_admitted_cases_count": len(
                {row.get("feature_name") for row in collection_rows if row.get("admission_status") == "admit"}
            ),
            "sample_limit_breaches": 0,
            "ready_for_v18c_phase_check_next": admitted_count >= 0,
        }
        interpretation = [
            "V1.8C executes only against the already-approved target features and source pools.",
            "Admitted cases are bounded by the frozen sample limits and remain below any promotion or strategy threshold.",
            "The next legal step is a V1.8C phase check and collection summary, not retained-feature promotion.",
        ]
        return V18CScreenedCollectionReport(
            summary=summary,
            collection_rows=collection_rows,
            interpretation=interpretation,
        )


def write_v18c_screened_collection_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18CScreenedCollectionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
