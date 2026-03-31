from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V18CScreenedCollectionProtocolReport:
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


class V18CScreenedCollectionProtocolAnalyzer:
    """Freeze the bounded protocol for screened collection."""

    def analyze(
        self,
        *,
        v18c_phase_charter_payload: dict[str, Any],
        v18a_breadth_entry_design_payload: dict[str, Any],
        v18b_feature_admission_gate_review_payload: dict[str, Any],
    ) -> V18CScreenedCollectionProtocolReport:
        charter_summary = dict(v18c_phase_charter_payload.get("summary", {}))
        entry_rows = list(v18a_breadth_entry_design_payload.get("entry_rows", []))
        gate_rows = list(v18b_feature_admission_gate_review_payload.get("review_rows", []))

        if not bool(charter_summary.get("do_open_v18c_now")):
            raise ValueError("V1.8C charter must be open before the screened collection protocol can be frozen.")

        entry_by_name = {str(row.get("feature_name", "")): row for row in entry_rows}
        protocol_rows: list[dict[str, Any]] = []
        for gate_row in gate_rows:
            feature_name = str(gate_row.get("feature_name", ""))
            if not bool(gate_row.get("admission_gate_ready")):
                continue
            entry_row = dict(entry_by_name.get(feature_name, {}))
            protocol_rows.append(
                {
                    "feature_name": feature_name,
                    "candidate_source_pool": entry_row.get("candidate_source_pool"),
                    "sample_limit": entry_row.get("sample_limit"),
                    "screening_mode": entry_row.get("breadth_entry_mode"),
                    "required_collection_artifacts": [
                        "admission_record",
                        "evidence_case_record",
                        "collection_summary_row",
                    ],
                }
            )

        protocol = {
            "target_feature_rows": protocol_rows,
            "collection_rules": [
                "screen candidates only from the frozen source pool",
                "respect current sample limits strictly",
                "record every admitted case with an admission record",
                "stop collection for a feature when its limit is reached or the screened pool is exhausted",
            ],
            "forbidden_actions": [
                "sample_limit_override",
                "generic_replay_growth",
                "retained_feature_promotion",
                "strategy_integration",
                "mixed_shortfall_collection",
            ],
        }
        summary = {
            "acceptance_posture": "freeze_v18c_screened_collection_protocol_v1",
            "target_feature_count": len(protocol_rows),
            "allow_retained_promotion_now": False,
            "ready_for_screened_collection_next": len(protocol_rows) > 0,
        }
        interpretation = [
            "V1.8C does not widen collection scope; it executes only against the two already approved breadth targets.",
            "The protocol keeps collection screened, sample-limited, and fully recordable.",
            "The next legal action is actual screened bounded collection, not promotion or new replay widening.",
        ]
        return V18CScreenedCollectionProtocolReport(
            summary=summary,
            protocol=protocol,
            interpretation=interpretation,
        )


def write_v18c_screened_collection_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V18CScreenedCollectionProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
