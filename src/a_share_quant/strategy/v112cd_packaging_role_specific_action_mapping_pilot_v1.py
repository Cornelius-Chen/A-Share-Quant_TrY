from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from a_share_quant.strategy.v112a_price_cycle_inference_v1 import TencentKlineClient


@dataclass(slots=True)
class V112CDPackagingRoleSpecificActionMappingPilotReport:
    summary: dict[str, Any]
    band_action_rows: list[dict[str, Any]]
    trade_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "band_action_rows": self.band_action_rows,
            "trade_rows": self.trade_rows,
            "comparison_rows": self.comparison_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CDPackagingRoleSpecificActionMappingPilotAnalyzer:
    DEFAULT_HOLDING_DAYS = 20
    DE_RISK_HOLDING_DAYS = 10
    TARGET_SYMBOL = "300757"
    TARGET_ROLE = "packaging_process_enabler"

    def analyze(
        self,
        *,
        bp_payload: dict[str, Any],
        bz_payload: dict[str, Any],
        bw_payload: dict[str, Any],
        neutral_payload: dict[str, Any],
    ) -> V112CDPackagingRoleSpecificActionMappingPilotReport:
        base_trade_rows = sorted(list(bp_payload.get("trade_rows", [])), key=lambda row: str(row.get("entry_date")))
        gate_rows = list(bp_payload.get("gate_decision_rows", []))
        if not base_trade_rows or not gate_rows:
            raise ValueError("V1.12CD requires frozen fusion trade rows and gate decision rows.")

        band_specs = self._load_packaging_band_specs(bz_payload=bz_payload)
        gate_feature_map = {(str(row.get("trade_date")), str(row.get("symbol"))): row for row in gate_rows}

        symbols = sorted({str(row.get("symbol")) for row in base_trade_rows})
        bar_cache = self._bar_cache(symbols=symbols)

        current_equity = 1.0
        trade_rows: list[dict[str, Any]] = []
        band_action_rows: list[dict[str, Any]] = []
        packaging_action_counts = {"entry_veto": 0, "de_risk": 0, "eligibility": 0}

        for trade in base_trade_rows:
            entry_date = str(trade.get("entry_date"))
            symbol = str(trade.get("symbol"))
            stage_family = str(trade.get("stage_family"))
            role_family = str(trade.get("role_family"))
            gate_row = gate_feature_map.get((entry_date, symbol), {})
            holding_days = self.DEFAULT_HOLDING_DAYS

            if symbol == self.TARGET_SYMBOL and role_family == self.TARGET_ROLE:
                band = self._predict_band(row=gate_row, band_specs=band_specs)
                if band == "veto_band":
                    packaging_action_counts["entry_veto"] += 1
                    band_action_rows.append(
                        {
                            "entry_date": entry_date,
                            "symbol": symbol,
                            "stage_family": stage_family,
                            "role_family": role_family,
                            "predicted_band": band,
                            "control_action": "entry_veto",
                        }
                    )
                    continue
                if band == "de_risk_band":
                    holding_days = self.DE_RISK_HOLDING_DAYS
                    packaging_action_counts["de_risk"] += 1
                    band_action_rows.append(
                        {
                            "entry_date": entry_date,
                            "symbol": symbol,
                            "stage_family": stage_family,
                            "role_family": role_family,
                            "predicted_band": band,
                            "control_action": "de_risk",
                        }
                    )
                else:
                    packaging_action_counts["eligibility"] += 1
                    band_action_rows.append(
                        {
                            "entry_date": entry_date,
                            "symbol": symbol,
                            "stage_family": stage_family,
                            "role_family": role_family,
                            "predicted_band": band,
                            "control_action": "eligibility",
                        }
                    )

            trade_path = self._trade_path(
                symbol=symbol,
                entry_date=entry_date,
                bars=bar_cache[symbol],
                holding_days=holding_days,
            )
            if not trade_path:
                continue

            entry_equity = current_equity
            peak_equity = entry_equity
            max_path_drawdown = 0.0
            for point in trade_path:
                path_equity = entry_equity * float(point["price_ratio"])
                peak_equity = max(peak_equity, path_equity)
                if peak_equity > 0.0:
                    max_path_drawdown = min(max_path_drawdown, path_equity / peak_equity - 1.0)
            current_equity = entry_equity * float(trade_path[-1]["price_ratio"])

            trade_rows.append(
                {
                    "entry_date": entry_date,
                    "exit_date": str(trade_path[-1]["trade_date"]),
                    "symbol": symbol,
                    "stage_family": stage_family,
                    "role_family": role_family,
                    "holding_days": holding_days,
                    "realized_forward_return": round(current_equity / entry_equity - 1.0, 4),
                    "path_max_drawdown": round(float(max_path_drawdown), 4),
                    "entry_equity": round(entry_equity, 4),
                    "exit_equity": round(current_equity, 4),
                }
            )

        total_return = current_equity - 1.0
        max_drawdown = min((float(row["path_max_drawdown"]) for row in trade_rows), default=0.0)
        positive_sum = sum(float(row["realized_forward_return"]) for row in trade_rows if float(row["realized_forward_return"]) > 0.0)
        negative_sum = sum(float(row["realized_forward_return"]) for row in trade_rows if float(row["realized_forward_return"]) < 0.0)
        profit_factor = positive_sum / abs(negative_sum) if negative_sum < 0.0 else math.inf

        bp_summary = dict(bp_payload.get("summary", {}))
        bw_summary = dict(bw_payload.get("summary", {}))
        neutral_summary = dict(neutral_payload.get("summary", {}))

        summary = {
            "acceptance_posture": "freeze_v112cd_packaging_role_specific_action_mapping_pilot_v1",
            "trade_count": len(trade_rows),
            "packaging_entry_veto_count": packaging_action_counts["entry_veto"],
            "packaging_de_risk_count": packaging_action_counts["de_risk"],
            "packaging_eligibility_count": packaging_action_counts["eligibility"],
            "total_return": round(total_return, 4),
            "max_drawdown": round(float(max_drawdown), 4),
            "profit_factor": round(float(profit_factor), 4) if profit_factor != math.inf else "inf",
            "bp_return_delta": round(total_return - float(bp_summary.get("total_return", 0.0)), 4),
            "bp_drawdown_delta": round(float(max_drawdown) - float(bp_summary.get("max_drawdown", 0.0)), 4),
            "bw_return_delta": round(total_return - float(bw_summary.get("total_return", 0.0)), 4),
            "bw_drawdown_delta": round(float(max_drawdown) - float(bw_summary.get("max_drawdown", 0.0)), 4),
            "neutral_return_delta": round(total_return - float(neutral_summary.get("total_return", 0.0)), 4),
            "neutral_drawdown_delta": round(float(max_drawdown) - float(neutral_summary.get("max_drawdown", 0.0)), 4),
            "formal_training_now": False,
            "formal_signal_generation_now": False,
            "recommended_next_posture": "use_packaging_role_specific_action_mapping_as_candidate_template_control",
        }
        comparison_rows = [
            {"comparison_name": "return_vs_bp", "baseline_value": bp_summary.get("total_return"), "pilot_value": summary["total_return"], "delta": summary["bp_return_delta"]},
            {"comparison_name": "drawdown_vs_bp", "baseline_value": bp_summary.get("max_drawdown"), "pilot_value": summary["max_drawdown"], "delta": summary["bp_drawdown_delta"]},
            {"comparison_name": "return_vs_bw", "baseline_value": bw_summary.get("total_return"), "pilot_value": summary["total_return"], "delta": summary["bw_return_delta"]},
            {"comparison_name": "drawdown_vs_bw", "baseline_value": bw_summary.get("max_drawdown"), "pilot_value": summary["max_drawdown"], "delta": summary["bw_drawdown_delta"]},
            {"comparison_name": "return_vs_neutral", "baseline_value": neutral_summary.get("total_return"), "pilot_value": summary["total_return"], "delta": summary["neutral_return_delta"]},
            {"comparison_name": "drawdown_vs_neutral", "baseline_value": neutral_summary.get("max_drawdown"), "pilot_value": summary["max_drawdown"], "delta": summary["neutral_drawdown_delta"]},
        ]
        interpretation = [
            "V1.12CD applies role-specific band edges to packaging_process_enabler trades only, while leaving laser-chip states as eligibility-only template members.",
            "The aim is to operationalize the three-layer action template on the one template-capable role that currently has empirical veto/de-risk/eligibility coverage.",
        ]
        return V112CDPackagingRoleSpecificActionMappingPilotReport(
            summary=summary,
            band_action_rows=band_action_rows,
            trade_rows=trade_rows,
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )

    def _load_packaging_band_specs(self, *, bz_payload: dict[str, Any]) -> dict[str, tuple[str, float]]:
        band_specs = {}
        for row in list(bz_payload.get("calibrated_band_rows", [])):
            if str(row.get("role_family")) != self.TARGET_ROLE:
                continue
            band_specs[str(row["feature_name"])] = (str(row["direction"]), float(row["calibrated_midpoint"]))
        if not band_specs:
            raise ValueError("V1.12CD requires packaging_process_enabler calibrated band specs from V1.12BZ.")
        return band_specs

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

    def _bar_cache(self, *, symbols: list[str]) -> dict[str, Any]:
        client = TencentKlineClient()
        cache = {}
        for symbol in symbols:
            frame = client.fetch_daily_bars(symbol).sort_values("date").reset_index(drop=True).copy()
            frame["trade_date"] = pd.to_datetime(frame["date"]).dt.strftime("%Y-%m-%d")
            cache[symbol] = frame
        return cache

    def _trade_path(self, *, symbol: str, entry_date: str, bars: Any, holding_days: int) -> list[dict[str, Any]]:
        matching = bars.index[bars["trade_date"] == entry_date].tolist()
        if not matching:
            return []
        start_idx = int(matching[0])
        end_idx = start_idx + holding_days
        if end_idx >= len(bars):
            return []
        entry_close = float(bars.iloc[start_idx]["close"])
        if entry_close == 0.0:
            return []
        rows = []
        for idx in range(start_idx, end_idx + 1):
            close = float(bars.iloc[idx]["close"])
            rows.append({"trade_date": str(bars.iloc[idx]["trade_date"]), "price_ratio": close / entry_close})
        return rows


def write_v112cd_packaging_role_specific_action_mapping_pilot_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CDPackagingRoleSpecificActionMappingPilotReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
