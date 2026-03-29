from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class EnvironmentBoundaryReport:
    source_report: str
    candidate_overview: list[dict[str, Any]]
    environment_winners: list[dict[str, Any]]
    boundary_summary: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_report": self.source_report,
            "candidate_overview": self.candidate_overview,
            "environment_winners": self.environment_winners,
            "boundary_summary": self.boundary_summary,
        }


def load_validation_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Validation report at {path} must decode to a mapping.")
    return payload


class EnvironmentBoundaryAnalyzer:
    """Summarize which finalists win which kinds of environments."""

    def analyze(self, payload: dict[str, Any]) -> EnvironmentBoundaryReport:
        extras = payload.get("extras", {})
        slice_summary = extras.get("slice_summary", [])
        leaderboard = extras.get("candidate_leaderboard", [])
        if not isinstance(slice_summary, list):
            raise ValueError("Validation report must contain a slice_summary list.")
        if not isinstance(leaderboard, list):
            raise ValueError("Validation report must contain a candidate_leaderboard list.")

        overview = self._candidate_overview(slice_summary=slice_summary, leaderboard=leaderboard)
        boundary_summary = self._boundary_summary(slice_summary=slice_summary, overview=overview)
        return EnvironmentBoundaryReport(
            source_report=str(payload.get("source_report", "time_slice_validation")),
            candidate_overview=overview,
            environment_winners=slice_summary,
            boundary_summary=boundary_summary,
        )

    def _candidate_overview(
        self,
        *,
        slice_summary: list[dict[str, Any]],
        leaderboard: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        overview: list[dict[str, Any]] = []
        candidate_metrics = {
            str(item["candidate_name"]): item
            for item in leaderboard
            if isinstance(item, dict) and item.get("candidate_name") is not None
        }
        candidate_names = sorted(candidate_metrics.keys())
        for candidate_name in candidate_names:
            best_total_return_envs = [
                item
                for item in slice_summary
                if str(item["best_total_return"]["candidate_name"]) == candidate_name
            ]
            best_capture_envs = [
                item
                for item in slice_summary
                if str(item["best_capture"]["candidate_name"]) == candidate_name
            ]
            lowest_drawdown_envs = [
                item
                for item in slice_summary
                if str(item["lowest_drawdown"]["candidate_name"]) == candidate_name
            ]
            metrics = candidate_metrics[candidate_name]
            overview.append(
                {
                    "candidate_name": candidate_name,
                    "composite_rank_score": metrics["composite_rank_score"],
                    "mean_total_return": metrics["mean_total_return"],
                    "mean_mainline_capture_ratio": metrics["mean_mainline_capture_ratio"],
                    "mean_max_drawdown": metrics["mean_max_drawdown"],
                    "positive_total_return_rows": metrics.get("positive_total_return_rows"),
                    "best_total_return_slice_count": len(best_total_return_envs),
                    "best_capture_slice_count": len(best_capture_envs),
                    "lowest_drawdown_slice_count": len(lowest_drawdown_envs),
                    "best_total_return_datasets": sorted(
                        {str(item["dataset_name"]) for item in best_total_return_envs}
                    ),
                    "best_capture_datasets": sorted(
                        {str(item["dataset_name"]) for item in best_capture_envs}
                    ),
                    "lowest_drawdown_datasets": sorted(
                        {str(item["dataset_name"]) for item in lowest_drawdown_envs}
                    ),
                }
            )
        return overview

    def _boundary_summary(
        self,
        *,
        slice_summary: list[dict[str, Any]],
        overview: list[dict[str, Any]],
    ) -> dict[str, Any]:
        most_stable = min(overview, key=lambda item: float(item["composite_rank_score"]))
        capture_specialist = max(overview, key=lambda item: int(item["best_capture_slice_count"]))
        drawdown_specialist = max(overview, key=lambda item: int(item["lowest_drawdown_slice_count"]))
        return {
            "slice_count": len(slice_summary),
            "most_stable_candidate": {
                "candidate_name": most_stable["candidate_name"],
                "composite_rank_score": most_stable["composite_rank_score"],
            },
            "capture_specialist": {
                "candidate_name": capture_specialist["candidate_name"],
                "best_capture_slice_count": capture_specialist["best_capture_slice_count"],
            },
            "drawdown_specialist": {
                "candidate_name": drawdown_specialist["candidate_name"],
                "lowest_drawdown_slice_count": drawdown_specialist["lowest_drawdown_slice_count"],
            },
            "interpretation": [
                "Most stable candidate is the best broad shared-default contender, not necessarily the specialist winner in every environment.",
                "Capture specialist is the candidate that wins the most slice-level capture environments.",
                "Drawdown specialist is the candidate that wins the most slice-level lowest-drawdown environments.",
            ],
        }


def write_environment_boundary_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: EnvironmentBoundaryReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
