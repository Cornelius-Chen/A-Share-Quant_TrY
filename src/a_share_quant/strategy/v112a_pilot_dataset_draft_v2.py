from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112APilotDatasetDraftV2Report:
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


class V112APilotDatasetDraftV2Analyzer:
    """Merge owner anchor plus price-cycle inference into a calibration-ready draft."""

    NAME_TRANSLATIONS = {
        "300308": "中际旭创",
        "300502": "新易盛",
        "300394": "天孚通信",
    }

    ROLE_TRANSLATIONS = {
        "300308": "龙头/核心受益股",
        "300502": "高弹性核心受益股",
        "300394": "上游核心器件平台受益股",
    }

    def analyze(
        self,
        *,
        pilot_dataset_draft_v1_payload: dict[str, Any],
        price_cycle_inference_payload: dict[str, Any],
    ) -> V112APilotDatasetDraftV2Report:
        base_rows = {
            str(row.get("symbol")): dict(row)
            for row in pilot_dataset_draft_v1_payload.get("dataset_rows", [])
        }
        inferred_map = {
            str(row.get("symbol")): dict(row)
            for row in price_cycle_inference_payload.get("inferred_rows", [])
        }

        dataset_rows: list[dict[str, Any]] = []
        ready_count = 0
        for symbol in ["300308", "300502", "300394"]:
            row = dict(base_rows[symbol])
            row["name"] = self.NAME_TRANSLATIONS.get(symbol, row.get("name"))
            row["final_role_label_cn"] = self.ROLE_TRANSLATIONS.get(symbol, row.get("final_role_label_cn"))
            if symbol in inferred_map:
                inferred = inferred_map[symbol]
                row["cycle_window"] = dict(inferred.get("suggested_cycle_window", {}))
                row["cycle_notes"] = str(inferred.get("notes_cn", ""))
                row["training_readiness"] = "price_inferred_waiting_owner_calibration"
                row["pending_fields"] = ["owner_cycle_confirmation"]
                row["owner_notes"] = "待 owner 校准价格推断窗口。"
            else:
                ready_count += 1
            dataset_rows.append(row)

        summary = {
            "acceptance_posture": "freeze_v112a_pilot_dataset_draft_v2_with_price_inference",
            "dataset_row_count": len(dataset_rows),
            "owner_anchor_ready_count": ready_count,
            "price_inferred_waiting_owner_calibration_count": len(dataset_rows) - ready_count,
            "ready_for_owner_calibration_next": True,
        }
        interpretation = [
            "V2 keeps the owner-corrected 300308 anchor untouched and fills the remaining symbols with price-only inferred cycle windows.",
            "This is still a calibration draft, not a training-ready freeze.",
            "The next high-value move is owner confirmation or correction on the two inferred windows.",
        ]
        return V112APilotDatasetDraftV2Report(
            summary=summary,
            dataset_rows=dataset_rows,
            interpretation=interpretation,
        )


def write_v112a_pilot_dataset_draft_v2_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APilotDatasetDraftV2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
