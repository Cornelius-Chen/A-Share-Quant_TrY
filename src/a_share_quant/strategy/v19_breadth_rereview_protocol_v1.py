from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V19BreadthRereviewProtocolReport:
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


class V19BreadthRereviewProtocolAnalyzer:
    """Freeze the bounded protocol for re-reviewing promotion judgment after new breadth evidence."""

    def analyze(
        self,
        *,
        v19_phase_charter_payload: dict[str, Any],
        v17_feature_promotion_gap_review_payload: dict[str, Any],
        v18c_screened_collection_payload: dict[str, Any],
    ) -> V19BreadthRereviewProtocolReport:
        charter_summary = dict(v19_phase_charter_payload.get("summary", {}))
        gap_rows = list(v17_feature_promotion_gap_review_payload.get("review_rows", []))
        collection_rows = list(v18c_screened_collection_payload.get("collection_rows", []))

        if not bool(charter_summary.get("do_open_v19_now")):
            raise ValueError("V1.9 charter must be open before the breadth re-review protocol can be frozen.")

        target_names = set(str(name) for name in charter_summary.get("target_feature_names", []))
        gap_by_name = {str(row.get("feature_name", "")): row for row in gap_rows}
        admitted_counts: dict[str, int] = {}
        for row in collection_rows:
            if row.get("admission_status") != "admit":
                continue
            name = str(row.get("feature_name", ""))
            admitted_counts[name] = admitted_counts.get(name, 0) + 1

        protocol_rows = []
        for feature_name in sorted(target_names):
            protocol_rows.append(
                {
                    "feature_name": feature_name,
                    "prior_primary_shortfall": gap_by_name.get(feature_name, {}).get("primary_shortfall"),
                    "new_admitted_case_count": admitted_counts.get(feature_name, 0),
                    "rereview_axes": [
                        "breadth_gap_reduction",
                        "updated_primary_shortfall",
                        "promotion_readiness_refresh",
                    ],
                }
            )

        protocol = {
            "target_feature_rows": protocol_rows,
            "bounded_rules": [
                "re-review must use only already collected breadth evidence",
                "re-review may update shortfall ordering but may not promote features",
                "re-review must preserve prior admissibility and stability boundaries",
                "re-review must stay below strategy integration",
            ],
            "forbidden_actions": [
                "retained_feature_promotion",
                "strategy_integration",
                "new_collection_inside_rereview",
                "new_refresh_opening",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v19_breadth_rereview_protocol_v1",
            "target_feature_count": len(protocol_rows),
            "allow_retained_promotion_now": False,
            "ready_for_per_feature_breadth_rereview_next": len(protocol_rows) > 0,
        }
        interpretation = [
            "V1.9 does not create more evidence; it refreshes promotion judgment using the breadth evidence already collected in V1.8C.",
            "The protocol allows shortfall re-ordering, but still forbids promotion and strategy integration.",
            "The next legal action is per-feature breadth re-review, not another collection round.",
        ]
        return V19BreadthRereviewProtocolReport(
            summary=summary,
            protocol=protocol,
            interpretation=interpretation,
        )


def write_v19_breadth_rereview_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V19BreadthRereviewProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
