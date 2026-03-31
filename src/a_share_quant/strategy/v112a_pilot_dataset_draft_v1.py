from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112APilotDatasetDraftReport:
    summary: dict[str, Any]
    dataset_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "dataset_rows": self.dataset_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112APilotDatasetDraftAnalyzer:
    """Freeze a partial pilot dataset draft after first owner corrections."""

    def analyze(
        self,
        *,
        owner_correction_integration_payload: dict[str, Any],
        training_protocol_payload: dict[str, Any],
    ) -> V112APilotDatasetDraftReport:
        integration_summary = dict(owner_correction_integration_payload.get("summary", {}))
        if not bool(integration_summary.get("ready_for_partial_pilot_dataset_draft_next")):
            raise ValueError("Owner correction integration must be ready before freezing the partial pilot dataset draft.")

        protocol = dict(training_protocol_payload.get("protocol", {}))
        label_set = list(protocol.get("label_set", []))

        dataset_rows = []
        resolved_training_row_count = 0
        for row in owner_correction_integration_payload.get("integrated_rows", []):
            cycle_defined = bool(row.get("cycle_window_defined"))
            if cycle_defined:
                resolved_training_row_count += 1
            dataset_rows.append(
                {
                    "symbol": row.get("symbol"),
                    "name": row.get("name"),
                    "final_role_label_cn": row.get("final_role_label_cn"),
                    "include_in_first_pilot": row.get("include_in_first_pilot"),
                    "cycle_window": row.get("cycle_window"),
                    "cycle_notes": row.get("cycle_notes"),
                    "label_set": label_set,
                    "training_readiness": "ready_for_next_labeling_step" if cycle_defined else "pending_more_owner_input",
                    "pending_fields": row.get("still_pending_fields", []),
                    "owner_notes": row.get("owner_notes"),
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112a_partial_pilot_dataset_draft_v1",
            "dataset_row_count": len(dataset_rows),
            "resolved_training_row_count": resolved_training_row_count,
            "pending_training_row_count": len(dataset_rows) - resolved_training_row_count,
            "ready_for_more_owner_corrections_next": True,
        }
        interpretation = [
            "The pilot dataset draft is allowed to be partial as long as readiness and pending fields are explicit.",
            "This gives the owner a concrete experimental surface instead of forcing full correctness before any draft exists.",
            "The next useful move is more owner correction on unresolved objects, not automatic model fitting.",
        ]
        return V112APilotDatasetDraftReport(summary=summary, dataset_rows=dataset_rows, interpretation=interpretation)


def write_v112a_pilot_dataset_draft_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APilotDatasetDraftReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
