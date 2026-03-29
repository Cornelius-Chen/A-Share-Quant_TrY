from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class DrawdownGapReport:
    source_report: str
    summary: dict[str, Any]
    dataset_strategy_summary: list[dict[str, Any]]
    weakest_slices: list[dict[str, Any]]
    weakest_rows: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "source_report": self.source_report,
            "summary": self.summary,
            "dataset_strategy_summary": self.dataset_strategy_summary,
            "weakest_slices": self.weakest_slices,
            "weakest_rows": self.weakest_rows,
        }


def load_validation_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Validation report at {path} must decode to a mapping.")
    return payload


class DrawdownGapAnalyzer:
    """Explain where a challenger still falls short on drawdown improvement."""

    def analyze(
        self,
        *,
        payload: dict[str, Any],
        incumbent_name: str,
        challenger_name: str,
    ) -> DrawdownGapReport:
        rows = payload.get("comparisons", [])
        if not isinstance(rows, list):
            raise ValueError("Validation report must contain a comparisons list.")

        paired_rows = self._pair_rows(
            rows=rows,
            incumbent_name=incumbent_name,
            challenger_name=challenger_name,
        )
        dataset_strategy_summary = self._dataset_strategy_summary(paired_rows)
        weakest_slices = self._weakest_slices(paired_rows)
        weakest_rows = self._weakest_rows(paired_rows)
        summary = self._summary(
            paired_rows=paired_rows,
            dataset_strategy_summary=dataset_strategy_summary,
            weakest_slices=weakest_slices,
        )
        return DrawdownGapReport(
            source_report=str(payload.get("source_report", "time_slice_validation")),
            summary=summary,
            dataset_strategy_summary=dataset_strategy_summary,
            weakest_slices=weakest_slices,
            weakest_rows=weakest_rows,
        )

    def _pair_rows(
        self,
        *,
        rows: list[dict[str, Any]],
        incumbent_name: str,
        challenger_name: str,
    ) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str, str], dict[str, dict[str, Any]]] = {}
        for row in rows:
            key = (
                str(row["dataset_name"]),
                str(row["slice_name"]),
                str(row["strategy_name"]),
            )
            grouped.setdefault(key, {})[str(row["candidate_name"])] = row

        paired_rows: list[dict[str, Any]] = []
        for (dataset_name, slice_name, strategy_name), candidates in sorted(grouped.items()):
            incumbent = candidates.get(incumbent_name)
            challenger = candidates.get(challenger_name)
            if incumbent is None or challenger is None:
                continue
            incumbent_summary = incumbent["summary"]
            challenger_summary = challenger["summary"]
            paired_rows.append(
                {
                    "dataset_name": dataset_name,
                    "slice_name": slice_name,
                    "slice_start": str(incumbent["slice_start"]),
                    "slice_end": str(incumbent["slice_end"]),
                    "strategy_name": strategy_name,
                    "drawdown_improvement": round(
                        float(incumbent_summary["max_drawdown"])
                        - float(challenger_summary["max_drawdown"]),
                        6,
                    ),
                    "total_return_delta": round(
                        float(challenger_summary["total_return"])
                        - float(incumbent_summary["total_return"]),
                        6,
                    ),
                    "capture_delta": round(
                        float(challenger_summary["mainline_capture_ratio"])
                        - float(incumbent_summary["mainline_capture_ratio"]),
                        6,
                    ),
                    "incumbent_max_drawdown": round(float(incumbent_summary["max_drawdown"]), 6),
                    "challenger_max_drawdown": round(float(challenger_summary["max_drawdown"]), 6),
                }
            )
        return paired_rows

    def _dataset_strategy_summary(self, paired_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in paired_rows:
            key = (str(row["dataset_name"]), str(row["strategy_name"]))
            grouped.setdefault(key, []).append(row)

        summary: list[dict[str, Any]] = []
        for (dataset_name, strategy_name), rows in sorted(grouped.items()):
            summary.append(
                {
                    "dataset_name": dataset_name,
                    "strategy_name": strategy_name,
                    "slice_count": len(rows),
                    "mean_drawdown_improvement": round(
                        sum(float(row["drawdown_improvement"]) for row in rows) / len(rows),
                        6,
                    ),
                    "mean_total_return_delta": round(
                        sum(float(row["total_return_delta"]) for row in rows) / len(rows),
                        6,
                    ),
                    "mean_capture_delta": round(
                        sum(float(row["capture_delta"]) for row in rows) / len(rows),
                        6,
                    ),
                    "negative_drawdown_slices": sum(
                        1 for row in rows if float(row["drawdown_improvement"]) < 0.0
                    ),
                    "weak_drawdown_slices": sum(
                        1 for row in rows if float(row["drawdown_improvement"]) < 0.0005
                    ),
                }
            )
        return sorted(
            summary,
            key=lambda item: (
                float(item["mean_drawdown_improvement"]),
                -float(item["mean_total_return_delta"]),
            ),
        )

    def _weakest_slices(self, paired_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in paired_rows:
            key = (str(row["dataset_name"]), str(row["slice_name"]))
            grouped.setdefault(key, []).append(row)

        weakest: list[dict[str, Any]] = []
        for (dataset_name, slice_name), rows in sorted(grouped.items()):
            weakest.append(
                {
                    "dataset_name": dataset_name,
                    "slice_name": slice_name,
                    "slice_start": rows[0]["slice_start"],
                    "slice_end": rows[0]["slice_end"],
                    "strategy_count": len(rows),
                    "mean_drawdown_improvement": round(
                        sum(float(row["drawdown_improvement"]) for row in rows) / len(rows),
                        6,
                    ),
                    "mean_total_return_delta": round(
                        sum(float(row["total_return_delta"]) for row in rows) / len(rows),
                        6,
                    ),
                    "mean_capture_delta": round(
                        sum(float(row["capture_delta"]) for row in rows) / len(rows),
                        6,
                    ),
                }
            )
        return sorted(
            weakest,
            key=lambda item: (
                float(item["mean_drawdown_improvement"]),
                float(item["mean_capture_delta"]),
            ),
        )[:8]

    def _weakest_rows(self, paired_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            paired_rows,
            key=lambda item: (
                float(item["drawdown_improvement"]),
                float(item["capture_delta"]),
            ),
        )[:12]

    def _summary(
        self,
        *,
        paired_rows: list[dict[str, Any]],
        dataset_strategy_summary: list[dict[str, Any]],
        weakest_slices: list[dict[str, Any]],
    ) -> dict[str, Any]:
        weakest_dataset_strategy = dataset_strategy_summary[0] if dataset_strategy_summary else None
        weakest_slice = weakest_slices[0] if weakest_slices else None
        return {
            "row_count": len(paired_rows),
            "dataset_count": len({str(row["dataset_name"]) for row in paired_rows}),
            "slice_count": len({(str(row["dataset_name"]), str(row["slice_name"])) for row in paired_rows}),
            "weakest_dataset_strategy": weakest_dataset_strategy,
            "weakest_slice": weakest_slice,
            "interpretation": [
                "Rows with the smallest or negative drawdown improvement are the most likely blockers for promotion.",
                "Dataset-strategy pairs with persistently weak drawdown improvement are better repair targets than global threshold search.",
                "If the weakest rows are concentrated in one dataset pack, the next cycle should focus there instead of reopening cross-pack tuning.",
            ],
        }


def write_drawdown_gap_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: DrawdownGapReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
