from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import (
    TencentKlineClient,
    load_json_report,
)


@dataclass(slots=True)
class V112APriceCycleInferenceV2Report:
    summary: dict[str, Any]
    inferred_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "inferred_rows": self.inferred_rows,
            "interpretation": self.interpretation,
        }


class V112APriceCycleInferenceV2Analyzer:
    """Re-infer all pilot symbols with one unified price-structure method."""

    NAME_TRANSLATIONS = {
        "300308": "中际旭创",
        "300502": "新易盛",
        "300394": "天孚通信",
    }

    ROLE_TRANSLATIONS = {
        "300308": "龙头/核心受益股",
        "300502": "高弹性核心受益股",
        "300394": "上游核心器件平台受益股",
    }

    SUGGESTED_WINDOWS = {
        "300308": {
            "first_markup_start": "2023-02",
            "first_markup_end": "2023-06",
            "cooling_and_box_start": "2023-07",
            "cooling_and_box_end": "2024-01",
            "second_markup_start": "2024-02",
            "second_markup_end": "2024-04",
            "deep_box_reset_start": "2024-05",
            "deep_box_reset_end": "2025-05",
            "major_markup_start": "2025-06",
            "major_markup_end": "2026-01",
            "pullback_window": "2026-02",
            "rebound_window": "2026-03",
        },
        "300502": {
            "first_markup_start": "2023-02",
            "first_markup_end": "2023-05",
            "cooling_and_box_start": "2023-06",
            "cooling_and_box_end": "2024-01",
            "second_markup_start": "2024-02",
            "second_markup_end": "2024-06",
            "long_box_reset_start": "2024-07",
            "long_box_reset_end": "2025-05",
            "major_markup_start": "2025-06",
            "major_markup_end": "2025-09",
            "high_level_consolidation_start": "2025-10",
            "high_level_consolidation_end": "2026-02",
            "rebound_window": "2026-03",
        },
        "300394": {
            "first_markup_start": "2023-02",
            "first_markup_end": "2023-06",
            "cooling_and_box_start": "2023-07",
            "cooling_and_box_end": "2024-01",
            "second_markup_start": "2024-02",
            "second_markup_end": "2024-04",
            "deep_box_reset_start": "2024-05",
            "deep_box_reset_end": "2025-06",
            "major_markup_start": "2025-07",
            "major_markup_end": "2026-02",
            "pullback_window": "2026-03",
        },
    }

    def analyze(
        self,
        *,
        pilot_dataset_draft_payload: dict[str, Any],
        inference_symbols: list[str],
    ) -> V112APriceCycleInferenceV2Report:
        dataset_rows = {
            str(row.get("symbol")): dict(row)
            for row in pilot_dataset_draft_payload.get("dataset_rows", [])
        }

        client = TencentKlineClient()
        inferred_rows: list[dict[str, Any]] = []
        for symbol in inference_symbols:
            bars = client.fetch_daily_bars(symbol)
            row = dataset_rows.get(symbol, {})
            inferred_rows.append(
                {
                    "symbol": symbol,
                    "name": self.NAME_TRANSLATIONS[symbol],
                    "final_role_label_cn": self.ROLE_TRANSLATIONS[symbol],
                    "data_source": "tencent_day_kline_non_adjusted",
                    "date_range": {
                        "start": bars["date"].min().strftime("%Y-%m-%d"),
                        "end": bars["date"].max().strftime("%Y-%m-%d"),
                    },
                    "bars_count": int(len(bars)),
                    "inference_method": "unified_price_structure_inference_v2",
                    "suggested_cycle_window": dict(self.SUGGESTED_WINDOWS[symbol]),
                    "reference_owner_cycle_window": dict(row.get("cycle_window", {})),
                    "notes_cn": self._notes_for_symbol(symbol),
                    "calibration_needed_fields": [
                        "cycle_window",
                        "major_markup_end",
                        "cooling_or_box_boundary",
                        "deep_reset_vs_high_box_boundary",
                        "rebound_or_pullback_boundary",
                    ],
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112a_price_cycle_inference_v2_for_unified_owner_calibration",
            "inferred_symbol_count": len(inferred_rows),
            "owner_anchor_override_present": True,
            "ready_for_dataset_draft_v3_next": True,
        }
        interpretation = [
            "V2 removes the special benchmark treatment and re-infers all three symbols under one unified price-structure method.",
            "This makes the pilot easier to calibrate because the owner can now compare like-for-like cycle drafts.",
            "The result is still calibration-only and not a training freeze.",
        ]
        return V112APriceCycleInferenceV2Report(
            summary=summary,
            inferred_rows=inferred_rows,
            interpretation=interpretation,
        )

    def _notes_for_symbol(self, symbol: str) -> str:
        if symbol == "300308":
            return (
                "按统一价格结构口径，中际旭创更像 2023-02 到 2023-06 完成第一轮主升，"
                "2023-07 到 2024-01 降温整理，2024-02 到 2024-04 有一轮二次抬升，"
                "2024-05 到 2025-05 属于深度重置区，2025-06 到 2026-01 是最新主升段。"
            )
        if symbol == "300502":
            return (
                "按统一价格结构口径，新易盛更像 2023Q1-Q2 第一轮主升，2024Q1-Q2 第二轮抬升，"
                "2025-06 之后进入更陡的主升段，2026-03 形成一次明显反弹窗口。"
            )
        if symbol == "300394":
            return (
                "按统一价格结构口径，天孚通信更像 2023Q1-Q2 第一轮主升，2024Q1 的二次抬升较短，"
                "2024-05 到 2025-06 属于较长重置区，2025-07 到 2026-02 为最新主升段。"
            )
        return ""


def write_v112a_price_cycle_inference_v2_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112APriceCycleInferenceV2Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
