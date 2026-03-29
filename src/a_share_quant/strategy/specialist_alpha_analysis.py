from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SpecialistAlphaReport:
    summary: dict[str, Any]
    specialist_summaries: list[dict[str, Any]]
    top_opportunities: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "specialist_summaries": self.specialist_summaries,
            "top_opportunities": self.top_opportunities,
            "interpretation": self.interpretation,
        }


def load_validation_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Validation report at {path} must decode to a mapping.")
    return payload


class SpecialistAlphaAnalyzer:
    """Find slice-level pockets where specialist branches beat both broad anchors."""

    def analyze(
        self,
        *,
        payload: dict[str, Any],
        anchors: list[str],
        specialists: list[dict[str, Any]],
    ) -> SpecialistAlphaReport:
        rows = payload.get("comparisons", [])
        if not isinstance(rows, list):
            raise ValueError("Validation report must contain a comparisons list.")

        grouped: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = {}
        for row in rows:
            key = (
                str(row["dataset_name"]),
                str(row["slice_name"]),
                str(row["strategy_name"]),
            )
            grouped.setdefault(key, {})[str(row["candidate_name"])] = row

        specialist_summaries: list[dict[str, Any]] = []
        top_opportunities: list[dict[str, Any]] = []
        for specialist in specialists:
            candidate_name = str(specialist["candidate_name"])
            primary_metric = str(specialist["primary_metric"])
            min_primary_advantage = float(specialist.get("min_primary_advantage", 0.0))
            max_secondary_penalty = float(specialist.get("max_secondary_penalty", 999.0))
            opportunity_rows: list[dict[str, Any]] = []

            for (dataset_name, slice_name, strategy_name), candidate_map in grouped.items():
                specialist_row = candidate_map.get(candidate_name)
                if specialist_row is None:
                    continue
                anchor_rows = [candidate_map.get(anchor) for anchor in anchors]
                if any(anchor_row is None for anchor_row in anchor_rows):
                    continue
                anchor_rows = [row for row in anchor_rows if row is not None]
                opportunity = self._build_opportunity_row(
                    dataset_name=dataset_name,
                    slice_name=slice_name,
                    strategy_name=strategy_name,
                    specialist_row=specialist_row,
                    anchor_rows=anchor_rows,
                    primary_metric=primary_metric,
                )
                if opportunity is None:
                    continue
                if float(opportunity["primary_advantage_vs_anchors"]) < min_primary_advantage:
                    continue
                if float(opportunity["secondary_penalty_vs_anchors"]) > max_secondary_penalty:
                    continue
                opportunity_rows.append(opportunity)

            opportunity_rows.sort(
                key=lambda item: (
                    -float(item["primary_advantage_vs_anchors"]),
                    float(item["secondary_penalty_vs_anchors"]),
                    float(item["total_return_delta_vs_anchors"]),
                )
            )
            top_opportunities.extend(
                [{**row, "specialist_candidate": candidate_name} for row in opportunity_rows[:5]]
            )
            specialist_summaries.append(
                {
                    "candidate_name": candidate_name,
                    "primary_metric": primary_metric,
                    "opportunity_count": len(opportunity_rows),
                    "best_opportunity": opportunity_rows[0] if opportunity_rows else None,
                    "top_datasets": sorted({str(row["dataset_name"]) for row in opportunity_rows}),
                    "top_slices": sorted({str(row["slice_name"]) for row in opportunity_rows}),
                }
            )

        top_opportunities.sort(
            key=lambda item: (
                item["specialist_candidate"],
                -float(item["primary_advantage_vs_anchors"]),
                float(item["secondary_penalty_vs_anchors"]),
            )
        )
        summary = {
            "anchor_count": len(anchors),
            "specialist_count": len(specialists),
            "top_specialist_by_opportunity_count": (
                max(
                    specialist_summaries,
                    key=lambda item: int(item["opportunity_count"]),
                )["candidate_name"]
                if specialist_summaries
                else None
            ),
        }
        interpretation = [
            "A specialist branch is most worth future research when it beats both broad anchors in its native metric inside a specific dataset-slice-strategy pocket.",
            "These opportunity pockets are not promotion evidence for the shared default. They are candidates for the next structural alpha cycle.",
            "Once a blocker line is frozen, the next high-value research question is where specialists still produce non-overlapping edge.",
        ]
        return SpecialistAlphaReport(
            summary=summary,
            specialist_summaries=specialist_summaries,
            top_opportunities=top_opportunities[:10],
            interpretation=interpretation,
        )

    def _build_opportunity_row(
        self,
        *,
        dataset_name: str,
        slice_name: str,
        strategy_name: str,
        specialist_row: dict[str, Any],
        anchor_rows: list[dict[str, Any]],
        primary_metric: str,
    ) -> dict[str, Any] | None:
        specialist_summary = specialist_row["summary"]
        anchor_summaries = [row["summary"] for row in anchor_rows]

        if primary_metric == "mainline_capture_ratio":
            primary_deltas = [
                float(specialist_summary["mainline_capture_ratio"]) - float(anchor["mainline_capture_ratio"])
                for anchor in anchor_summaries
            ]
            secondary_penalties = [
                float(specialist_summary["max_drawdown"]) - float(anchor["max_drawdown"])
                for anchor in anchor_summaries
            ]
        elif primary_metric == "max_drawdown":
            primary_deltas = [
                float(anchor["max_drawdown"]) - float(specialist_summary["max_drawdown"])
                for anchor in anchor_summaries
            ]
            secondary_penalties = [
                float(anchor["total_return"]) - float(specialist_summary["total_return"])
                for anchor in anchor_summaries
            ]
        else:
            raise ValueError(f"Unsupported primary metric: {primary_metric}")

        if min(primary_deltas) <= 0.0:
            return None

        total_return_deltas = [
            float(specialist_summary["total_return"]) - float(anchor["total_return"])
            for anchor in anchor_summaries
        ]
        return {
            "dataset_name": dataset_name,
            "slice_name": slice_name,
            "strategy_name": strategy_name,
            "primary_advantage_vs_anchors": round(min(primary_deltas), 6),
            "secondary_penalty_vs_anchors": round(max(secondary_penalties), 6),
            "total_return_delta_vs_anchors": round(min(total_return_deltas), 6),
        }


def write_specialist_alpha_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: SpecialistAlphaReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
