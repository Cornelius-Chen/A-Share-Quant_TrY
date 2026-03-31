from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112AOwnerCorrectionIntegrationReport:
    summary: dict[str, Any]
    integrated_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "integrated_rows": self.integrated_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112AOwnerCorrectionIntegrationAnalyzer:
    """Integrate owner corrections into the first pilot sheet."""

    ROLE_TRANSLATIONS = {
        "300308": "龙头/核心受益股",
        "300502": "高弹性核心受益股",
        "300394": "上游核心器件平台受益股",
    }

    def analyze(
        self,
        *,
        label_review_sheet_payload: dict[str, Any],
        owner_corrections: dict[str, Any],
    ) -> V112AOwnerCorrectionIntegrationReport:
        review_rows = list(label_review_sheet_payload.get("review_rows", []))
        correction_map = dict(owner_corrections.get("symbol_corrections", {}))

        integrated_rows: list[dict[str, Any]] = []
        resolved_cycle_count = 0
        for row in review_rows:
            symbol = str(row.get("symbol", ""))
            correction = dict(correction_map.get(symbol, {}))

            cycle_window = dict(correction.get("cycle_window", {}))
            cycle_defined = bool(cycle_window)
            if cycle_defined:
                resolved_cycle_count += 1

            integrated_rows.append(
                {
                    "symbol": symbol,
                    "name": row.get("name"),
                    "pool_role_guess": row.get("pool_role_guess"),
                    "final_role_label_cn": self.ROLE_TRANSLATIONS.get(symbol, "待定"),
                    "include_in_first_pilot": bool(correction.get("include_in_first_pilot", row.get("include_in_first_pilot_guess", True))),
                    "cycle_window_defined": cycle_defined,
                    "cycle_window": cycle_window,
                    "cycle_notes": str(correction.get("cycle_notes", "")),
                    "object_missing_or_extra_review": str(
                        correction.get("object_missing_or_extra_review", row.get("object_missing_or_extra_review", "owner_review_needed"))
                    ),
                    "role_correction_status": "integrated_role_translation",
                    "cycle_window_correction_status": (
                        "integrated_owner_window" if cycle_defined else row.get("cycle_window_correction_status", "owner_review_needed")
                    ),
                    "owner_notes": str(correction.get("owner_notes", row.get("owner_notes", ""))),
                    "still_pending_fields": [
                        field
                        for field, flag in [
                            ("cycle_window", not cycle_defined),
                            ("owner_notes", not str(correction.get("owner_notes", row.get("owner_notes", ""))).strip()),
                        ]
                        if flag
                    ],
                }
            )

        summary = {
            "acceptance_posture": "integrate_v112a_owner_corrections_v1",
            "object_count": len(integrated_rows),
            "resolved_cycle_count": resolved_cycle_count,
            "pending_cycle_count": len(integrated_rows) - resolved_cycle_count,
            "ready_for_partial_pilot_dataset_draft_next": True,
        }
        interpretation = [
            "Owner corrections are integrated incrementally rather than waiting for every field to be fully specified.",
            "This lets the pilot move from a blank review sheet to a partially resolved dataset draft while keeping unresolved fields explicit.",
            "The next step is to freeze a partial pilot dataset draft that shows what is ready and what still needs correction.",
        ]
        return V112AOwnerCorrectionIntegrationReport(
            summary=summary,
            integrated_rows=integrated_rows,
            interpretation=interpretation,
        )


def write_v112a_owner_correction_integration_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112AOwnerCorrectionIntegrationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
