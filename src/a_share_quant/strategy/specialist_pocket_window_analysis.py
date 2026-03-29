from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class SpecialistPocketWindowReport:
    summary: dict[str, Any]
    top_window_edges: list[dict[str, Any]]
    symbol_summary: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "top_window_edges": self.top_window_edges,
            "symbol_summary": self.symbol_summary,
            "interpretation": self.interpretation,
        }


def load_validation_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Validation report at {path} must decode to a mapping.")
    return payload


class SpecialistPocketWindowAnalyzer:
    """Explain which windows create a specialist edge inside one pocket."""

    def analyze(
        self,
        *,
        payload: dict[str, Any],
        dataset_name: str,
        slice_name: str,
        strategy_name: str,
        specialist_candidate: str,
        anchor_candidates: list[str],
    ) -> SpecialistPocketWindowReport:
        rows = payload.get("comparisons", [])
        if not isinstance(rows, list):
            raise ValueError("Validation report must contain a comparisons list.")

        pocket_rows = {
            str(row["candidate_name"]): row
            for row in rows
            if str(row["dataset_name"]) == dataset_name
            and str(row["slice_name"]) == slice_name
            and str(row["strategy_name"]) == strategy_name
        }
        specialist_row = pocket_rows.get(specialist_candidate)
        if specialist_row is None:
            raise ValueError("Specialist row not found in validation report.")
        anchor_rows = [pocket_rows.get(name) for name in anchor_candidates]
        if any(row is None for row in anchor_rows):
            raise ValueError("One or more anchor rows not found in validation report.")
        anchor_rows = [row for row in anchor_rows if row is not None]

        specialist_windows = {
            str(item["window_id"]): item for item in specialist_row.get("window_breakdown", [])
        }
        anchor_window_maps = [
            {str(item["window_id"]): item for item in row.get("window_breakdown", [])}
            for row in anchor_rows
        ]

        top_window_edges: list[dict[str, Any]] = []
        symbol_scores: dict[str, dict[str, float | int]] = {}
        for window_id, specialist_window in specialist_windows.items():
            anchor_windows = [window_map.get(window_id) for window_map in anchor_window_maps]
            if any(window is None for window in anchor_windows):
                continue
            anchor_windows = [window for window in anchor_windows if window is not None]
            specialist_capture = float(specialist_window["capture_ratio"])
            anchor_captures = [float(window["capture_ratio"]) for window in anchor_windows]
            min_capture_edge = round(specialist_capture - max(anchor_captures), 6)
            if min_capture_edge <= 0.0:
                continue
            both_anchors_missed = all(bool(window["missed"]) for window in anchor_windows)
            symbol = str(specialist_window["symbol"])
            capturable_return = float(specialist_window["capturable_return"])
            top_window_edges.append(
                {
                    "window_id": window_id,
                    "symbol": symbol,
                    "capturable_return": capturable_return,
                    "specialist_capture_ratio": specialist_capture,
                    "anchor_capture_ratios": anchor_captures,
                    "min_capture_edge": min_capture_edge,
                    "both_anchors_missed": both_anchors_missed,
                }
            )
            entry = symbol_scores.setdefault(
                symbol,
                {
                    "improved_window_count": 0,
                    "both_anchors_missed_count": 0,
                    "total_capture_edge": 0.0,
                    "total_capturable_return": 0.0,
                },
            )
            entry["improved_window_count"] = int(entry["improved_window_count"]) + 1
            entry["both_anchors_missed_count"] = int(entry["both_anchors_missed_count"]) + int(both_anchors_missed)
            entry["total_capture_edge"] = round(float(entry["total_capture_edge"]) + min_capture_edge, 6)
            entry["total_capturable_return"] = round(
                float(entry["total_capturable_return"]) + max(capturable_return, 0.0),
                6,
            )

        top_window_edges.sort(
            key=lambda item: (
                -float(item["min_capture_edge"]),
                -float(item["capturable_return"]),
            )
        )
        symbol_summary = sorted(
            (
                {
                    "symbol": symbol,
                    **metrics,
                }
                for symbol, metrics in symbol_scores.items()
            ),
            key=lambda item: (
                -float(item["total_capture_edge"]),
                -int(item["both_anchors_missed_count"]),
            ),
        )
        summary = {
            "dataset_name": dataset_name,
            "slice_name": slice_name,
            "strategy_name": strategy_name,
            "specialist_candidate": specialist_candidate,
            "anchor_candidates": anchor_candidates,
            "improved_window_count": len(top_window_edges),
            "both_anchors_missed_window_count": sum(
                1 for item in top_window_edges if bool(item["both_anchors_missed"])
            ),
            "top_symbol": symbol_summary[0]["symbol"] if symbol_summary else None,
        }
        interpretation = [
            "A specialist pocket is most actionable when it improves windows that both broad anchors miss entirely.",
            "Window-level edges are stronger research leads than aggregate pocket scores because they tell the repo which symbols and dates to replay next.",
            "If a specialist only improves already-partially-captured windows, it may be less valuable than a branch that opens entirely new windows.",
        ]
        return SpecialistPocketWindowReport(
            summary=summary,
            top_window_edges=top_window_edges[:12],
            symbol_summary=symbol_summary[:10],
            interpretation=interpretation,
        )


def write_specialist_pocket_window_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: SpecialistPocketWindowReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
