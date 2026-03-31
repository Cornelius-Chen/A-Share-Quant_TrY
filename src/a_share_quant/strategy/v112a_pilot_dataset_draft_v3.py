from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112APilotDatasetDraftV3Report:
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


class V112APilotDatasetDraftV3Analyzer:
    """Freeze a unified-calibration draft after re-inferring all three symbols."""

    def analyze(
        self,
        *,
        pilot_dataset_draft_v1_payload: dict[str, Any],
        price_cycle_inference_v2_payload: dict[str, Any],
    ) -> V112APilotDatasetDraftV3Report:
        base_rows = {
            str(row.get("symbol")): dict(row)
            for row in pilot_dataset_draft_v1_payload.get("dataset_rows", [])
        }
        inferred_map = {
            str(row.get("symbol")): dict(row)
            for row in price_cycle_inference_v2_payload.get("inferred_rows", [])
        }

        dataset_rows: list[dict[str, Any]] = []
        for symbol in ["300308", "300502", "300394"]:
            base = dict(base_rows[symbol])
            inferred = dict(inferred_map[symbol])
            dataset_rows.append(
                {
                    "symbol": symbol,
                    "name": inferred.get("name", base.get("name")),
                    "final_role_label_cn": inferred.get("final_role_label_cn", base.get("final_role_label_cn")),
                    "include_in_first_pilot": base.get("include_in_first_pilot", True),
                    "cycle_window": dict(inferred.get("suggested_cycle_window", {})),
                    "cycle_notes": str(inferred.get("notes_cn", "")),
                    "reference_owner_cycle_window": dict(inferred.get("reference_owner_cycle_window", {})),
                    "label_set": list(base.get("label_set", [])),
                    "training_readiness": "unified_price_inferred_waiting_owner_calibration",
                    "pending_fields": ["owner_cycle_confirmation"],
                    "owner_notes": "待 owner 统一口径校准价格推断窗口。",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112a_pilot_dataset_draft_v3_with_unified_price_inference",
            "dataset_row_count": len(dataset_rows),
            "unified_price_inferred_count": len(dataset_rows),
            "ready_for_owner_calibration_next": True,
        }
        interpretation = [
            "V3 removes the special human anchor and lets the owner calibrate all three symbols under one unified price-structure draft.",
            "This should reduce label-style mismatch before the first pilot training freeze.",
            "The next useful move is owner calibration, not more automatic inference.",
        ]
        return V112APilotDatasetDraftV3Report(
            summary=summary,
            dataset_rows=dataset_rows,
            interpretation=interpretation,
        )


def write_v112a_pilot_dataset_draft_v3_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APilotDatasetDraftV3Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
