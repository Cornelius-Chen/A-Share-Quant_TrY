from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112BPilotDatasetFreezeReport:
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


class V112BPilotDatasetFreezeAnalyzer:
    """Freeze the accepted unified draft into the first trainable pilot dataset."""

    NAME_MAP = {
        "300308": "中际旭创",
        "300502": "新易盛",
        "300394": "天孚通信",
    }

    ROLE_MAP = {
        "300308": "龙头/核心受益股",
        "300502": "高弹性核心受益股",
        "300394": "上游核心器件平台受益股",
    }

    def analyze(
        self,
        *,
        phase_charter_payload: dict[str, Any],
        pilot_dataset_draft_payload: dict[str, Any],
    ) -> V112BPilotDatasetFreezeReport:
        charter_summary = dict(phase_charter_payload.get("summary", {}))
        if not bool(charter_summary.get("ready_for_dataset_freeze_next")):
            raise ValueError("V1.12B dataset freeze requires an open V1.12B charter.")

        input_rows = list(pilot_dataset_draft_payload.get("dataset_rows", []))
        dataset_rows: list[dict[str, Any]] = []
        for row in input_rows:
            symbol = str(row.get("symbol"))
            cycle_window = dict(row.get("cycle_window", {}))
            dataset_rows.append(
                {
                    "symbol": symbol,
                    "name": self.NAME_MAP.get(symbol, str(row.get("name", ""))),
                    "final_role_label_cn": self.ROLE_MAP.get(symbol, str(row.get("final_role_label_cn", ""))),
                    "include_in_first_pilot": True,
                    "cycle_window": cycle_window,
                    "cycle_month_span": len(cycle_window),
                    "label_set": list(row.get("label_set", [])),
                    "training_readiness": "frozen_for_report_only_baseline",
                    "owner_acceptance_status": "accepted_via_conversation",
                    "owner_notes": "已按统一口径接受，可进入第一轮 report-only baseline。",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112b_first_trainable_pilot_dataset_v1",
            "dataset_row_count": len(dataset_rows),
            "frozen_symbol_count": sum(1 for row in dataset_rows if bool(row.get("include_in_first_pilot"))),
            "all_rows_owner_accepted": True,
            "ready_for_baseline_readout_next": True,
        }
        interpretation = [
            "This is the first point where the optical-link pilot draft becomes a trainable dataset rather than a review sheet.",
            "The freeze intentionally keeps the object set narrow at three core names.",
            "The next lawful move is a report-only baseline readout under the already-frozen V1.12 protocol.",
        ]
        return V112BPilotDatasetFreezeReport(
            summary=summary,
            dataset_rows=dataset_rows,
            interpretation=interpretation,
        )


def write_v112b_pilot_dataset_freeze_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BPilotDatasetFreezeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
