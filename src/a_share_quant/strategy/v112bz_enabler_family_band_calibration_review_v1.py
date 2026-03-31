from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient


@dataclass(slots=True)
class V112BZEnablerFamilyBandCalibrationReviewReport:
    summary: dict[str, Any]
    role_calibration_rows: list[dict[str, Any]]
    calibrated_band_rows: list[dict[str, Any]]
    diagnostic_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "role_calibration_rows": self.role_calibration_rows,
            "calibrated_band_rows": self.calibrated_band_rows,
            "diagnostic_rows": self.diagnostic_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112BZEnablerFamilyBandCalibrationReviewAnalyzer:
    TARGET_SYMBOLS = {"688498", "688313", "300757"}

    def analyze(
        self,
        *,
        bx_payload: dict[str, Any],
        bp_payload: dict[str, Any],
        az_payload: dict[str, Any],
    ) -> V112BZEnablerFamilyBandCalibrationReviewReport:
        base_band_specs = {
            str(row["feature_name"]): (str(row["direction"]), float(row["balance_midpoint"]))
            for row in list(bx_payload.get("band_rows", []))
        }
        if not base_band_specs:
            raise ValueError("V1.12BZ requires base band specs from V1.12BX.")

        role_map = {
            str(row["symbol"]): str(row["role_family"])
            for row in list(az_payload.get("training_layer_rows", []))
        }
        gate_rows = [row for row in list(bp_payload.get("gate_decision_rows", [])) if str(row.get("symbol")) in self.TARGET_SYMBOLS]
        if not gate_rows:
            raise ValueError("V1.12BZ requires gate rows for target symbols.")

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
            sample = {
                "trade_date": str(row["trade_date"]),
                "symbol": str(row["symbol"]),
                "role_family": role_map.get(str(row["symbol"]), "unknown"),
                "actual_band": self._actual_band(
                    forward_return_20d=float(outcome["forward_return_20d"]),
                    max_drawdown_20d=float(outcome["max_drawdown_20d"]),
                ),
            }
            for feature_name in base_band_specs:
                sample[feature_name] = float(row.get(feature_name, 0.0))
            sample_rows.append(sample)

        role_groups: dict[str, list[dict[str, Any]]] = {}
        for row in sample_rows:
            role_groups.setdefault(str(row["role_family"]), []).append(row)

        role_calibration_rows: list[dict[str, Any]] = []
        calibrated_band_rows: list[dict[str, Any]] = []
        diagnostic_rows: list[dict[str, Any]] = []

        for role_family, rows in sorted(role_groups.items()):
            before_correct = sum(
                1 for row in rows if self._predict_band(row=row, band_specs=base_band_specs) == str(row["actual_band"])
            )
            before_accuracy = before_correct / len(rows)

            if before_accuracy >= 0.9:
                role_calibration_rows.append(
                    {
                        "role_family": role_family,
                        "sample_count": len(rows),
                        "pre_calibration_accuracy": round(before_accuracy, 4),
                        "post_calibration_accuracy": round(before_accuracy, 4),
                        "calibration_posture": "adopt_transferred_band_unchanged",
                    }
                )
                continue

            if role_family == "packaging_process_enabler":
                role_band_specs = self._calibrate_role_band(rows=rows, base_band_specs=base_band_specs)
                after_correct = sum(
                    1 for row in rows if self._predict_band(row=row, band_specs=role_band_specs) == str(row["actual_band"])
                )
                after_accuracy = after_correct / len(rows)
                role_calibration_rows.append(
                    {
                        "role_family": role_family,
                        "sample_count": len(rows),
                        "pre_calibration_accuracy": round(before_accuracy, 4),
                        "post_calibration_accuracy": round(after_accuracy, 4),
                        "calibration_posture": "adopt_role_specific_band_edges",
                    }
                )
                for feature_name, (direction, midpoint) in role_band_specs.items():
                    calibrated_band_rows.append(
                        {
                            "role_family": role_family,
                            "feature_name": feature_name,
                            "direction": direction,
                            "calibrated_midpoint": round(midpoint, 6),
                        }
                    )
                continue

            diagnostic_rows.append(
                {
                    "role_family": role_family,
                    "sample_count": len(rows),
                    "pre_calibration_accuracy": round(before_accuracy, 4),
                    "diagnostic_posture": "isolate_role_for_separate_direction_review",
                    "reading": "Transferred direction set is insufficiently aligned for direct family-wide calibration.",
                }
            )
            role_calibration_rows.append(
                {
                    "role_family": role_family,
                    "sample_count": len(rows),
                    "pre_calibration_accuracy": round(before_accuracy, 4),
                    "post_calibration_accuracy": round(before_accuracy, 4),
                    "calibration_posture": "do_not_transfer_unmodified",
                }
            )

        summary = {
            "acceptance_posture": "freeze_v112bz_enabler_family_band_calibration_review_v1",
            "role_count": len(role_calibration_rows),
            "role_specific_calibration_count": sum(
                1 for row in role_calibration_rows if str(row["calibration_posture"]) == "adopt_role_specific_band_edges"
            ),
            "unchanged_transfer_count": sum(
                1 for row in role_calibration_rows if str(row["calibration_posture"]) == "adopt_transferred_band_unchanged"
            ),
            "isolated_role_count": sum(
                1 for row in role_calibration_rows if str(row["calibration_posture"]) == "do_not_transfer_unmodified"
            ),
            "recommended_next_posture": "promote_packaging_and_laser_as_candidate_template_paths_and_isolate_silicon_review",
        }
        interpretation = [
            "V1.12BZ shows that the 4-direction band transfers at the direction level, but edge calibration must still be role-specific.",
            "Laser-chip states can keep the transferred band, packaging-process-enabler needs local edge calibration, and silicon-photonics should be isolated for separate review.",
        ]
        return V112BZEnablerFamilyBandCalibrationReviewReport(
            summary=summary,
            role_calibration_rows=role_calibration_rows,
            calibrated_band_rows=calibrated_band_rows,
            diagnostic_rows=diagnostic_rows,
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
        return {"forward_return_20d": forward_return_20d, "max_drawdown_20d": max_drawdown_20d}

    def _actual_band(self, *, forward_return_20d: float, max_drawdown_20d: float) -> str:
        if forward_return_20d <= -0.08 or max_drawdown_20d <= -0.20:
            return "veto_band"
        if forward_return_20d >= 0.05 and max_drawdown_20d > -0.20:
            return "eligibility_band"
        return "de_risk_band"

    def _predict_band(self, *, row: dict[str, Any], band_specs: dict[str, tuple[str, float]]) -> str:
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

    def _calibrate_role_band(
        self,
        *,
        rows: list[dict[str, Any]],
        base_band_specs: dict[str, tuple[str, float]],
    ) -> dict[str, tuple[str, float]]:
        calibrated: dict[str, tuple[str, float]] = {}
        veto_rows = [row for row in rows if str(row["actual_band"]) == "veto_band"]
        eligibility_rows = [row for row in rows if str(row["actual_band"]) == "eligibility_band"]
        for feature_name, (direction, base_midpoint) in base_band_specs.items():
            if not veto_rows or not eligibility_rows:
                calibrated[feature_name] = (direction, base_midpoint)
                continue
            veto_mean = sum(float(row[feature_name]) for row in veto_rows) / len(veto_rows)
            eligibility_mean = sum(float(row[feature_name]) for row in eligibility_rows) / len(eligibility_rows)
            calibrated[feature_name] = (direction, (veto_mean + eligibility_mean) / 2.0)
        return calibrated


def write_v112bz_enabler_family_band_calibration_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112BZEnablerFamilyBandCalibrationReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
