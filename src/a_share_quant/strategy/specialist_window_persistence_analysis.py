from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SpecialistWindowPersistenceReport:
    summary: dict[str, Any]
    persistence_edge: dict[str, Any] | None
    anchor_divergence: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "persistence_edge": self.persistence_edge,
            "anchor_divergence": self.anchor_divergence,
            "interpretation": self.interpretation,
        }


def load_timeline_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Timeline report at {path} must decode to a mapping.")
    return payload


class SpecialistWindowPersistenceAnalyzer:
    """Explain when a specialist keeps a window alive while anchors churn out."""

    def analyze(
        self,
        *,
        payload: dict[str, Any],
        strategy_name: str,
        specialist_candidate: str,
        anchor_candidates: list[str],
        window_start: str,
        window_end: str,
    ) -> SpecialistWindowPersistenceReport:
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

        persistence_edge: dict[str, Any] | None = None
        anchor_divergence: list[dict[str, Any]] = []
        for day in specialist_days:
            trade_date = str(day["trade_date"])
            if int(day.get("position_qty", 0)) <= 0:
                continue
            if bool(day.get("exit_should_exit")):
                continue
            anchor_days = [day_map.get(trade_date) for day_map in anchor_day_maps]
            if any(anchor_day is None for anchor_day in anchor_days):
                continue
            anchor_days = [anchor_day for anchor_day in anchor_days if anchor_day is not None]
            divergent = [
                (anchor_name, anchor_day)
                for anchor_name, anchor_day in zip(anchor_candidates, anchor_days, strict=False)
                if bool(anchor_day.get("exit_should_exit"))
                or "sell" in [str(item) for item in anchor_day.get("emitted_actions", [])]
            ]
            if not divergent:
                continue

            persistence_edge = {
                "trade_date": trade_date,
                "specialist_candidate": specialist_candidate,
                "specialist_position_qty": day.get("position_qty"),
                "specialist_holding_should_hold": day.get("holding_should_hold"),
                "specialist_holding_health_score": day.get("holding_health_score"),
                "specialist_exit_should_exit": day.get("exit_should_exit"),
                "specialist_exit_reason": day.get("exit_reason"),
                "specialist_assignment_layer": day.get("assignment_layer"),
                "specialist_assignment_reason": day.get("assignment_reason"),
            }
            for anchor_name, anchor_day in divergent:
                anchor_divergence.append(
                    {
                        "candidate_name": anchor_name,
                        "trade_date": trade_date,
                        "position_qty": anchor_day.get("position_qty"),
                        "holding_should_hold": anchor_day.get("holding_should_hold"),
                        "holding_health_score": anchor_day.get("holding_health_score"),
                        "exit_should_exit": anchor_day.get("exit_should_exit"),
                        "exit_reason": anchor_day.get("exit_reason"),
                        "emitted_actions": list(anchor_day.get("emitted_actions", [])),
                        "assignment_layer": anchor_day.get("assignment_layer"),
                        "assignment_reason": anchor_day.get("assignment_reason"),
                    }
                )
            break

        summary = {
            "strategy_name": strategy_name,
            "specialist_candidate": specialist_candidate,
            "anchor_candidates": anchor_candidates,
            "window_start": window_start,
            "window_end": window_end,
            "specialist_preserved_window": persistence_edge is not None,
            "persistence_trade_date": persistence_edge["trade_date"] if persistence_edge is not None else None,
        }
        interpretation = [
            "A persistence edge is different from an opening edge: the specialist already has the position and simply refuses to churn out when anchors do.",
            "The cleanest persistence cases happen when the specialist still says hold while anchors emit sell on the same date.",
            "If the specialist and anchors all entered the window together, then persistence usually matters more than entry logic for the resulting capture edge.",
        ]
        return SpecialistWindowPersistenceReport(
            summary=summary,
            persistence_edge=persistence_edge,
            anchor_divergence=anchor_divergence,
            interpretation=interpretation,
        )


def write_specialist_window_persistence_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: SpecialistWindowPersistenceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
