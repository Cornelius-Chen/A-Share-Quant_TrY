from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a mapping payload in {path}.")
    return payload


@dataclass(slots=True)
class BaselineCaptureDiagnosticResult:
    summary: dict[str, Any]
    strategy_deltas: list[dict[str, Any]]
    slice_deltas: list[dict[str, Any]]
    top_window_regressions: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "strategy_deltas": self.strategy_deltas,
            "slice_deltas": self.slice_deltas,
            "top_window_regressions": self.top_window_regressions,
        }


class BaselineCaptureDiagnostic:
    """Explain where a challenger loses baseline-pack capture versus the incumbent."""

    def analyze(
        self,
        *,
        comparison_payload: dict[str, Any],
        incumbent_name: str,
        challenger_name: str,
        dataset_name: str,
        slice_payload: dict[str, Any] | None = None,
    ) -> BaselineCaptureDiagnosticResult:
        comparisons = comparison_payload.get("comparisons", [])
        if not isinstance(comparisons, list):
            raise ValueError("Comparison payload is missing valid comparison rows.")

        baseline_rows = [
            row
            for row in comparisons
            if isinstance(row, dict) and str(row.get("dataset_name")) == dataset_name
        ]
        strategy_deltas = self._strategy_deltas(
            rows=baseline_rows,
            incumbent_name=incumbent_name,
            challenger_name=challenger_name,
        )
        top_window_regressions = self._top_window_regressions(
            rows=baseline_rows,
            incumbent_name=incumbent_name,
            challenger_name=challenger_name,
        )

        slice_deltas: list[dict[str, Any]] = []
        if slice_payload is not None:
            slice_comparisons = slice_payload.get("comparisons", [])
            if not isinstance(slice_comparisons, list):
                raise ValueError("Slice payload is missing valid comparison rows.")
            baseline_slice_rows = [
                row
                for row in slice_comparisons
                if isinstance(row, dict) and str(row.get("dataset_name")) == dataset_name
            ]
            slice_deltas = self._slice_deltas(
                rows=baseline_slice_rows,
                incumbent_name=incumbent_name,
                challenger_name=challenger_name,
            )

        mean_capture_regression = round(
            sum(item["capture_regression"] for item in strategy_deltas) / len(strategy_deltas),
            6,
        ) if strategy_deltas else 0.0
        worst_strategy = max(
            strategy_deltas,
            key=lambda item: item["capture_regression"],
        ) if strategy_deltas else None
        worst_slice = max(
            slice_deltas,
            key=lambda item: item["capture_regression"],
        ) if slice_deltas else None

        summary = {
            "dataset_name": dataset_name,
            "incumbent_name": incumbent_name,
            "challenger_name": challenger_name,
            "strategy_count": len(strategy_deltas),
            "slice_count": len(slice_deltas),
            "mean_capture_regression": mean_capture_regression,
            "worst_strategy": worst_strategy,
            "worst_slice": worst_slice,
            "top_window_regression_count": len(top_window_regressions),
        }
        return BaselineCaptureDiagnosticResult(
            summary=summary,
            strategy_deltas=strategy_deltas,
            slice_deltas=slice_deltas,
            top_window_regressions=top_window_regressions,
        )

    def _strategy_deltas(
        self,
        *,
        rows: list[dict[str, Any]],
        incumbent_name: str,
        challenger_name: str,
    ) -> list[dict[str, Any]]:
        grouped = self._group_rows(rows=rows, key_fields=("strategy_name",))
        deltas: list[dict[str, Any]] = []
        for (strategy_name,), pair in sorted(grouped.items()):
            incumbent_row = pair.get(incumbent_name)
            challenger_row = pair.get(challenger_name)
            if incumbent_row is None or challenger_row is None:
                continue
            incumbent_summary = incumbent_row["summary"]
            challenger_summary = challenger_row["summary"]
            capture_regression = max(
                0.0,
                float(incumbent_summary["mainline_capture_ratio"])
                - float(challenger_summary["mainline_capture_ratio"]),
            )
            deltas.append(
                {
                    "strategy_name": strategy_name,
                    "incumbent_capture": round(float(incumbent_summary["mainline_capture_ratio"]), 6),
                    "challenger_capture": round(float(challenger_summary["mainline_capture_ratio"]), 6),
                    "capture_delta": round(
                        float(challenger_summary["mainline_capture_ratio"])
                        - float(incumbent_summary["mainline_capture_ratio"]),
                        6,
                    ),
                    "capture_regression": round(capture_regression, 6),
                    "incumbent_total_return": round(float(incumbent_summary["total_return"]), 6),
                    "challenger_total_return": round(float(challenger_summary["total_return"]), 6),
                    "total_return_delta": round(
                        float(challenger_summary["total_return"])
                        - float(incumbent_summary["total_return"]),
                        6,
                    ),
                    "missed_mainline_delta": int(challenger_summary["missed_mainline_count"])
                    - int(incumbent_summary["missed_mainline_count"]),
                }
            )
        return deltas

    def _slice_deltas(
        self,
        *,
        rows: list[dict[str, Any]],
        incumbent_name: str,
        challenger_name: str,
    ) -> list[dict[str, Any]]:
        grouped = self._group_rows(rows=rows, key_fields=("slice_name", "strategy_name"))
        by_slice: dict[str, list[dict[str, Any]]] = {}
        for (slice_name, strategy_name), pair in grouped.items():
            incumbent_row = pair.get(incumbent_name)
            challenger_row = pair.get(challenger_name)
            if incumbent_row is None or challenger_row is None:
                continue
            incumbent_capture = float(incumbent_row["summary"]["mainline_capture_ratio"])
            challenger_capture = float(challenger_row["summary"]["mainline_capture_ratio"])
            by_slice.setdefault(slice_name, []).append(
                {
                    "strategy_name": strategy_name,
                    "capture_delta": challenger_capture - incumbent_capture,
                    "capture_regression": max(0.0, incumbent_capture - challenger_capture),
                }
            )

        rows_out: list[dict[str, Any]] = []
        for slice_name, values in sorted(by_slice.items()):
            worst = max(values, key=lambda item: item["capture_regression"])
            rows_out.append(
                {
                    "slice_name": slice_name,
                    "mean_capture_delta": round(
                        sum(item["capture_delta"] for item in values) / len(values),
                        6,
                    ),
                    "capture_regression": round(
                        sum(item["capture_regression"] for item in values) / len(values),
                        6,
                    ),
                    "worst_strategy_name": worst["strategy_name"],
                    "worst_strategy_capture_regression": round(worst["capture_regression"], 6),
                }
            )
        return rows_out

    def _top_window_regressions(
        self,
        *,
        rows: list[dict[str, Any]],
        incumbent_name: str,
        challenger_name: str,
    ) -> list[dict[str, Any]]:
        grouped = self._group_rows(rows=rows, key_fields=("strategy_name",))
        regressions: list[dict[str, Any]] = []
        for (strategy_name,), pair in grouped.items():
            incumbent_row = pair.get(incumbent_name)
            challenger_row = pair.get(challenger_name)
            if incumbent_row is None or challenger_row is None:
                continue
            incumbent_windows = {
                str(item["window_id"]): item
                for item in incumbent_row.get("window_breakdown", [])
                if isinstance(item, dict)
            }
            challenger_windows = {
                str(item["window_id"]): item
                for item in challenger_row.get("window_breakdown", [])
                if isinstance(item, dict)
            }
            for window_id, incumbent_window in incumbent_windows.items():
                challenger_window = challenger_windows.get(window_id)
                if challenger_window is None:
                    continue
                incumbent_capture = float(incumbent_window["capture_ratio"])
                challenger_capture = float(challenger_window["capture_ratio"])
                regression = incumbent_capture - challenger_capture
                if regression <= 0:
                    continue
                regressions.append(
                    {
                        "strategy_name": strategy_name,
                        "window_id": window_id,
                        "symbol": incumbent_window.get("symbol"),
                        "start_date": incumbent_window.get("start_date"),
                        "end_date": incumbent_window.get("end_date"),
                        "capturable_return": round(float(incumbent_window["capturable_return"]), 6),
                        "incumbent_capture_ratio": round(incumbent_capture, 6),
                        "challenger_capture_ratio": round(challenger_capture, 6),
                        "capture_regression": round(regression, 6),
                    }
                )
        return sorted(
            regressions,
            key=lambda item: (
                -float(item["capture_regression"]),
                -float(item["capturable_return"]),
            ),
        )[:20]

    def _group_rows(
        self,
        *,
        rows: list[dict[str, Any]],
        key_fields: tuple[str, ...],
    ) -> dict[tuple[str, ...], dict[str, dict[str, Any]]]:
        grouped: dict[tuple[str, ...], dict[str, dict[str, Any]]] = {}
        for row in rows:
            key = tuple(str(row[field]) for field in key_fields)
            candidate_name = str(row["candidate_name"])
            grouped.setdefault(key, {})[candidate_name] = row
        return grouped


def write_baseline_capture_diagnostic(
    *,
    reports_dir: Path,
    report_name: str,
    result: BaselineCaptureDiagnosticResult,
    extras: dict[str, Any] | None = None,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    payload = result.as_dict()
    if extras:
        payload["extras"] = extras
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
    return output_path
