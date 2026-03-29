from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SpecialistWindowOpeningReport:
    summary: dict[str, Any]
    opening_edge: dict[str, Any] | None
    anchor_blockers: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "opening_edge": self.opening_edge,
            "anchor_blockers": self.anchor_blockers,
            "interpretation": self.interpretation,
        }


def load_timeline_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Timeline report at {path} must decode to a mapping.")
    return payload


class SpecialistWindowOpeningAnalyzer:
    """Explain which daily state opens a specialist-owned capture window."""

    def analyze(
        self,
        *,
        payload: dict[str, Any],
        strategy_name: str,
        specialist_candidate: str,
        anchor_candidates: list[str],
        window_start: str,
        window_end: str,
    ) -> SpecialistWindowOpeningReport:
        candidate_records = payload.get("candidate_records", [])
        if not isinstance(candidate_records, list):
            raise ValueError("Timeline report must contain candidate_records.")

        record_map = {
            str(record["candidate_name"]): record
            for record in candidate_records
            if str(record["strategy_name"]) == strategy_name
        }
        specialist_record = record_map.get(specialist_candidate)
        if specialist_record is None:
            raise ValueError("Specialist record not found for requested strategy.")
        anchor_records = [record_map.get(name) for name in anchor_candidates]
        if any(record is None for record in anchor_records):
            raise ValueError("One or more anchor candidate records are missing.")
        anchor_records = [record for record in anchor_records if record is not None]

        specialist_days = [
            day
            for day in specialist_record.get("daily_records", [])
            if window_start <= str(day["trade_date"]) <= window_end
        ]
        anchor_day_maps = [
            {
                str(day["trade_date"]): day
                for day in record.get("daily_records", [])
                if window_start <= str(day["trade_date"]) <= window_end
            }
            for record in anchor_records
        ]

        opening_edge: dict[str, Any] | None = None
        anchor_blockers: list[dict[str, Any]] = []
        for day in specialist_days:
            trade_date = str(day["trade_date"])
            specialist_actions = [str(item) for item in day.get("emitted_actions", [])]
            if "buy" not in specialist_actions:
                continue
            anchor_days = [day_map.get(trade_date) for day_map in anchor_day_maps]
            if any(anchor_day is None for anchor_day in anchor_days):
                continue
            anchor_days = [anchor_day for anchor_day in anchor_days if anchor_day is not None]
            if any("buy" in [str(item) for item in anchor_day.get("emitted_actions", [])] for anchor_day in anchor_days):
                continue

            opening_edge = {
                "trade_date": trade_date,
                "specialist_candidate": specialist_candidate,
                "specialist_assignment_layer": day.get("assignment_layer"),
                "specialist_assignment_reason": day.get("assignment_reason"),
                "specialist_permission_allowed": day.get("permission_allowed"),
                "specialist_triggered_entries": list(day.get("triggered_entries", [])),
                "specialist_passed_filters": list(day.get("passed_filters", [])),
            }
            for anchor_name, anchor_day in zip(anchor_candidates, anchor_days, strict=False):
                anchor_blockers.append(
                    {
                        "candidate_name": anchor_name,
                        "trade_date": trade_date,
                        "permission_allowed": anchor_day.get("permission_allowed"),
                        "assignment_layer": anchor_day.get("assignment_layer"),
                        "assignment_reason": anchor_day.get("assignment_reason"),
                        "triggered_entries": list(anchor_day.get("triggered_entries", [])),
                        "passed_filters": list(anchor_day.get("passed_filters", [])),
                        "emitted_actions": list(anchor_day.get("emitted_actions", [])),
                    }
                )
            break

        summary = {
            "strategy_name": strategy_name,
            "specialist_candidate": specialist_candidate,
            "anchor_candidates": anchor_candidates,
            "window_start": window_start,
            "window_end": window_end,
            "specialist_opened_window": opening_edge is not None,
            "opening_trade_date": opening_edge["trade_date"] if opening_edge is not None else None,
        }
        interpretation = [
            "A specialist-owned window is most interesting when permission, filters, and entries are already aligned but the hierarchy layer is still different.",
            "If anchors and specialist share the same permission path, then a pure assignment-layer upgrade is a strong candidate for the true opening edge.",
            "The first specialist-only buy date is usually more actionable than later exit differences because it explains how the window was opened in the first place.",
        ]
        return SpecialistWindowOpeningReport(
            summary=summary,
            opening_edge=opening_edge,
            anchor_blockers=anchor_blockers,
            interpretation=interpretation,
        )


def write_specialist_window_opening_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: SpecialistWindowOpeningReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
