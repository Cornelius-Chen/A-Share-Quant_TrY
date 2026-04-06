from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_theme_symbol_hit_replay_v1 import (
    MaterializeAShareInternalHotNewsThemeSymbolHitReplayV1,
)
from a_share_quant.info_center.automation.pipeline_jobs.materialize_a_share_internal_hot_news_sina_theme_probe_v1 import (
    MaterializeAShareInternalHotNewsSinaThemeProbeV1,
)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    materialized_rows = rows or [{"row_state": "empty"}]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(materialized_rows[0].keys()))
        writer.writeheader()
        writer.writerows(materialized_rows)


def _ratio(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "0.0000"
    return f"{numerator / denominator:.4f}"


@dataclass(slots=True)
class MaterializedAShareInternalHotNewsSecondSourceProbeComparisonV1:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]


class MaterializeAShareInternalHotNewsSecondSourceProbeComparisonV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_path = (
            repo_root
            / "data"
            / "derived"
            / "info_center"
            / "time_slices"
            / "a_share_internal_hot_news_second_source_probe_comparison_v1.csv"
        )

    def materialize(self) -> MaterializedAShareInternalHotNewsSecondSourceProbeComparisonV1:
        cls_result = MaterializeAShareInternalHotNewsThemeSymbolHitReplayV1(self.repo_root).materialize()
        sina_result = MaterializeAShareInternalHotNewsSinaThemeProbeV1(self.repo_root).materialize()

        cls_sample = int(cls_result.summary["sample_row_count"])
        cls_theme_hit = int(cls_result.summary["theme_hit_count"])
        cls_symbol_route = int(cls_result.summary["theme_hit_with_symbol_watch_count"])
        cls_unique_theme = int(cls_result.summary["unique_primary_theme_count"])

        sina_sample = int(sina_result.summary["sample_row_count"])
        sina_theme_hit = int(sina_result.summary["theme_hit_count"])
        sina_symbol_route = int(sina_result.summary["theme_hit_with_symbol_route_count"])
        sina_unique_theme = int(sina_result.summary["unique_primary_theme_count"])

        row = {
            "comparison_id": "internal_hot_news_second_source_probe_latest",
            "primary_source_name": "cls_telegraph",
            "probe_source_name": "sina_7x24",
            "primary_sample_row_count": str(cls_sample),
            "probe_sample_row_count": str(sina_sample),
            "primary_theme_hit_count": str(cls_theme_hit),
            "probe_theme_hit_count": str(sina_theme_hit),
            "primary_theme_hit_rate": _ratio(cls_theme_hit, cls_sample),
            "probe_theme_hit_rate": _ratio(sina_theme_hit, sina_sample),
            "primary_symbol_route_count": str(cls_symbol_route),
            "probe_symbol_route_count": str(sina_symbol_route),
            "primary_symbol_route_rate": _ratio(cls_symbol_route, cls_sample),
            "probe_symbol_route_rate": _ratio(sina_symbol_route, sina_sample),
            "primary_unique_theme_count": str(cls_unique_theme),
            "probe_unique_theme_count": str(sina_unique_theme),
            "theme_hit_delta": str(sina_theme_hit - cls_theme_hit),
            "symbol_route_delta": str(sina_symbol_route - cls_symbol_route),
            "unique_theme_delta": str(sina_unique_theme - cls_unique_theme),
            "probe_value_state": (
                "probe_lift_confirmed"
                if sina_theme_hit > cls_theme_hit and sina_unique_theme > cls_unique_theme
                else "probe_lift_not_yet_confirmed"
            ),
            "comparison_state": "second_source_probe_compared",
        }

        _write_csv(self.output_path, [row])
        summary = {
            "primary_sample_row_count": cls_sample,
            "probe_sample_row_count": sina_sample,
            "primary_theme_hit_count": cls_theme_hit,
            "probe_theme_hit_count": sina_theme_hit,
            "primary_symbol_route_count": cls_symbol_route,
            "probe_symbol_route_count": sina_symbol_route,
            "primary_unique_theme_count": cls_unique_theme,
            "probe_unique_theme_count": sina_unique_theme,
            "probe_value_state": row["probe_value_state"],
            "authoritative_output": "a_share_internal_hot_news_second_source_probe_comparison_materialized",
        }
        return MaterializedAShareInternalHotNewsSecondSourceProbeComparisonV1(summary=summary, rows=[row])


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareInternalHotNewsSecondSourceProbeComparisonV1(repo_root).materialize()
    print(result.summary["authoritative_output"])


if __name__ == "__main__":
    main()
