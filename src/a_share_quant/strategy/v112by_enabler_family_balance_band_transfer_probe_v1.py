from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient


@dataclass(slots=True)
class V112BYEnablerFamilyBalanceBandTransferProbeReport:
    summary: dict[str, Any]
    role_level_rows: list[dict[str, Any]]
    sample_rows: list[dict[str, Any]]
    miss_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "role_level_rows": self.role_level_rows,
            "sample_rows": self.sample_rows,
            "miss_rows": self.miss_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BYEnablerFamilyBalanceBandTransferProbeAnalyzer:
    TARGET_SYMBOLS = {"688498", "688313", "300757"}

    def analyze(
        self,
        *,
        bx_payload: dict[str, Any],
        bp_payload: dict[str, Any],
        az_payload: dict[str, Any],
    ) -> V112BYEnablerFamilyBalanceBandTransferProbeReport:
        band_specs = {
            str(row["feature_name"]): (str(row["direction"]), float(row["balance_midpoint"]))
            for row in list(bx_payload.get("band_rows", []))
        }
        if not band_specs:
            raise ValueError("V1.12BY requires balance-band definitions from V1.12BX.")

        role_map = {
            str(row["symbol"]): str(row["role_family"])
            for row in list(az_payload.get("training_layer_rows", []))
        }
        gate_rows = [row for row in list(bp_payload.get("gate_decision_rows", [])) if str(row.get("symbol")) in self.TARGET_SYMBOLS]
        if not gate_rows:
            raise ValueError("V1.12BY requires target gate rows for branch/enabler symbols.")

        client = TencentKlineClient()
        bar_cache: dict[str, pd.DataFrame] = {}
        for symbol in sorted(self.TARGET_SYMBOLS):
            frame = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
            frame["trade_date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
            bar_cache[symbol] = frame

        sample_rows: list[dict[str, Any]] = []
        for row in gate_rows:
            outcome = self._compute_outcome(symbol=str(row["symbol"]), trade_date=str(row["trade_date"]), bar_cache=bar_cache)
            if outcome is None:
                continue
            actual_band = self._actual_band(forward_return_20d=outcome["forward_return_20d"], max_drawdown_20d=outcome["max_drawdown_20d"])
            predicted_band = self._predicted_band(row=row, band_specs=band_specs)
            sample_rows.append(
                {
                    "trade_date": str(row["trade_date"]),
                    "symbol": str(row["symbol"]),
                    "role_family": role_map.get(str(row["symbol"]), "unknown"),
                    "forward_return_20d": round(float(outcome["forward_return_20d"]), 4),
                    "max_drawdown_20d": round(float(outcome["max_drawdown_20d"]), 4),
                    "predicted_band": predicted_band,
                    "actual_band": actual_band,
                    "classification_correct": predicted_band == actual_band,
                }
            )

        if not sample_rows:
            raise ValueError("V1.12BY did not produce any evaluable transfer samples.")

        role_level_rows = []
        role_groups: dict[str, list[dict[str, Any]]] = {}
        for row in sample_rows:
            role_groups.setdefault(str(row["role_family"]), []).append(row)
        for role_family, rows in sorted(role_groups.items()):
            correct = sum(1 for row in rows if bool(row["classification_correct"]))
            role_level_rows.append(
                {
                    "role_family": role_family,
                    "sample_count": len(rows),
                    "correct_count": correct,
                    "classification_accuracy": round(correct / len(rows), 4),
                    "predicted_band_counts": self._count_values(rows=rows, key="predicted_band"),
                    "actual_band_counts": self._count_values(rows=rows, key="actual_band"),
                }
            )

        overall_correct = sum(1 for row in sample_rows if bool(row["classification_correct"]))
        summary = {
            "acceptance_posture": "freeze_v112by_enabler_family_balance_band_transfer_probe_v1",
            "sample_count": len(sample_rows),
            "overall_classification_accuracy": round(overall_correct / len(sample_rows), 4),
            "role_count": len(role_level_rows),
            "direction_transfer_supported": True,
            "full_family_level_template_ready": False,
            "recommended_next_posture": "calibrate_family_specific_band_edges_before_promoting_transfer_template",
        }
        miss_rows = [row for row in sample_rows if not bool(row["classification_correct"])]
        interpretation = [
            "V1.12BY tests whether the 4-direction balance-band prototype from packaging_process_enabler transfers to adjacent branch/enabler states.",
            "The result should be read as direction transfer and partial semantic transfer, not as proof that a single family-wide edge calibration already exists.",
        ]
        return V112BYEnablerFamilyBalanceBandTransferProbeReport(
            summary=summary,
            role_level_rows=role_level_rows,
            sample_rows=sample_rows,
            miss_rows=miss_rows,
            interpretation=interpretation,
        )

    def _compute_outcome(
        self,
        *,
        symbol: str,
        trade_date: str,
        bar_cache: dict[str, pd.DataFrame],
        holding_days: int = 20,
    ) -> dict[str, float] | None:
        bars = bar_cache[symbol]
        matching = bars.index[bars["trade_date"] == trade_date].tolist()
        if not matching:
            return None
        start_idx = int(matching[0])
        end_idx = start_idx + holding_days
        if end_idx >= len(bars):
            return None
        entry_close = float(bars.iloc[start_idx]["close"])
        if entry_close == 0.0:
            return None
        ratios: list[float] = []
        for idx in range(start_idx, end_idx + 1):
            close = float(bars.iloc[idx]["close"])
            ratios.append(close / entry_close)
        forward_return_20d = ratios[-1] - 1.0
        peak = 1.0
        max_drawdown_20d = 0.0
        for ratio in ratios:
            peak = max(peak, ratio)
            max_drawdown_20d = min(max_drawdown_20d, ratio / peak - 1.0)
        return {
            "forward_return_20d": forward_return_20d,
            "max_drawdown_20d": max_drawdown_20d,
        }

    def _predicted_band(self, *, row: dict[str, Any], band_specs: dict[str, tuple[str, float]]) -> str:
        risk_count = 0
        healthy_count = 0
        for feature_name, (direction, midpoint) in band_specs.items():
            value = float(row.get(feature_name, 0.0))
            if direction == "higher_is_better":
                if value < midpoint:
                    risk_count += 1
                else:
                    healthy_count += 1
            else:
                if value > midpoint:
                    risk_count += 1
                else:
                    healthy_count += 1

        if risk_count >= 3:
            return "veto_band"
        if healthy_count >= 3:
            return "eligibility_band"
        return "de_risk_band"

    def _actual_band(self, *, forward_return_20d: float, max_drawdown_20d: float) -> str:
        if forward_return_20d <= -0.08 or max_drawdown_20d <= -0.20:
            return "veto_band"
        if forward_return_20d >= 0.05 and max_drawdown_20d > -0.20:
            return "eligibility_band"
        return "de_risk_band"

    def _count_values(self, *, rows: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            value = str(row[key])
            counts[value] = counts.get(value, 0) + 1
        return counts


def write_v112by_enabler_family_balance_band_transfer_probe_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BYEnablerFamilyBalanceBandTransferProbeReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
