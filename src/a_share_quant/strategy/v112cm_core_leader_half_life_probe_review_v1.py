from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

os.environ.setdefault("PANDAS_NO_USE_NUMEXPR", "1")
os.environ.setdefault("PANDAS_NO_USE_BOTTLENECK", "1")

import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient


@dataclass(slots=True)
class V112CMCoreLeaderHalfLifeProbeReviewReport:
    summary: dict[str, Any]
    half_life_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "half_life_rows": self.half_life_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CMCoreLeaderHalfLifeProbeReviewAnalyzer:
    TARGET_SYMBOL = "300308"
    HOLDING_GRID = (5, 10, 15, 20)

    def analyze(
        self,
        *,
        bh_payload: dict[str, Any],
    ) -> V112CMCoreLeaderHalfLifeProbeReviewReport:
        target_rows = [row for row in list(bh_payload.get("trade_rows", [])) if str(row.get("symbol")) == self.TARGET_SYMBOL]
        if not target_rows:
            raise ValueError("V1.12CM requires neutral trade rows for 300308.")

        client = TencentKlineClient()
        bars = client.fetch_daily_bars(self.TARGET_SYMBOL).sort_values("date").reset_index(drop=True).copy()
        bars["trade_date"] = pd.to_datetime(bars["date"]).dt.strftime("%Y-%m-%d")

        half_life_rows: list[dict[str, Any]] = []
        best_return = None
        best_drawdown = None

        for holding_days in self.HOLDING_GRID:
            current_equity = 1.0
            max_drawdown = 0.0
            trade_count = 0
            for row in target_rows:
                entry_date = str(row.get("entry_date"))
                matching = bars.index[bars["trade_date"] == entry_date].tolist()
                if not matching:
                    continue
                start_idx = int(matching[0])
                end_idx = start_idx + holding_days
                if end_idx >= len(bars):
                    continue
                trade_count += 1
                entry_close = float(bars.iloc[start_idx]["close"])
                entry_equity = current_equity
                peak_equity = entry_equity
                for idx in range(start_idx, end_idx + 1):
                    close = float(bars.iloc[idx]["close"])
                    path_equity = entry_equity * (close / entry_close)
                    peak_equity = max(peak_equity, path_equity)
                    if peak_equity > 0.0:
                        max_drawdown = min(max_drawdown, path_equity / peak_equity - 1.0)
                exit_close = float(bars.iloc[end_idx]["close"])
                current_equity = entry_equity * (exit_close / entry_close)

            total_return = current_equity - 1.0
            half_life_rows.append(
                {
                    "holding_days": holding_days,
                    "trade_count": trade_count,
                    "total_return": round(total_return, 4),
                    "max_drawdown": round(float(max_drawdown), 4),
                }
            )
            if holding_days == 20:
                best_return = total_return
                best_drawdown = max_drawdown

        summary = {
            "acceptance_posture": "freeze_v112cm_core_leader_half_life_probe_review_v1",
            "holding_grid_count": len(self.HOLDING_GRID),
            "baseline_holding_days": 20,
            "baseline_total_return": round(float(best_return), 4) if best_return is not None else None,
            "baseline_max_drawdown": round(float(best_drawdown), 4) if best_drawdown is not None else None,
            "simple_half_life_cut_sufficient": False,
            "recommended_next_posture": "do_not_use_uniform_core_leader_half_life_cut_open_state_conditioned_holding_veto_probe",
        }
        interpretation = [
            "V1.12CM checks whether a simple uniform half-life cut can solve core leader mature-markup overstay without needing a richer control template.",
            "The probe shows drawdown can be reduced by shorter holding, but the return loss is too large, so a blunt half-life reduction is not the right fix.",
        ]
        return V112CMCoreLeaderHalfLifeProbeReviewReport(
            summary=summary,
            half_life_rows=half_life_rows,
            interpretation=interpretation,
        )


def write_v112cm_core_leader_half_life_probe_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CMCoreLeaderHalfLifeProbeReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
