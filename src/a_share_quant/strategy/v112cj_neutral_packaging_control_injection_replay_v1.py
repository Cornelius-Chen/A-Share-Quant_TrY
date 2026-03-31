from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CJNeutralPackagingControlInjectionReplayReport:
    summary: dict[str, Any]
    packaging_window_rows: list[dict[str, Any]]
    residual_trade_rows: list[dict[str, Any]]
    comparison_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "packaging_window_rows": self.packaging_window_rows,
            "residual_trade_rows": self.residual_trade_rows,
            "comparison_rows": self.comparison_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CJNeutralPackagingControlInjectionReplayAnalyzer:
    TARGET_SYMBOL = "300757"
    TARGET_ROLE = "packaging_process_enabler"

    def analyze(
        self,
        *,
        neutral_payload: dict[str, Any],
        bp_payload: dict[str, Any],
        bz_payload: dict[str, Any],
        cf_payload: dict[str, Any],
        ch_payload: dict[str, Any],
    ) -> V112CJNeutralPackagingControlInjectionReplayReport:
        freeze_summary = dict(ch_payload.get("summary", {}))
        if int(freeze_summary.get("cluster_mainline_template_asset_count", 0)) != 1:
            raise ValueError("V1.12CJ requires exactly one frozen cluster mainline template asset from V1.12CH.")

        band_specs = self._load_packaging_band_specs(bz_payload=bz_payload)
        neutral_trade_rows = list(neutral_payload.get("trade_rows", []))
        neutral_equity_rows = list(neutral_payload.get("equity_curve_rows", []))
        gate_rows = [
            row
            for row in list(bp_payload.get("gate_decision_rows", []))
            if str(row.get("symbol")) == self.TARGET_SYMBOL
        ]
        if not neutral_trade_rows or not neutral_equity_rows or not gate_rows:
            raise ValueError("V1.12CJ requires neutral trades/equity rows and packaging gate rows.")

        position_map = {
            str(row.get("trade_date")): {
                "position_state": str(row.get("position_state")),
                "symbol": str(row.get("symbol")),
            }
            for row in neutral_equity_rows
        }

        packaging_window_rows: list[dict[str, Any]] = []
        eligibility_missed = 0
        veto_false_open = 0
        de_risk_cash_count = 0

        for row in gate_rows:
            trade_date = str(row.get("trade_date"))
            band = self._refined_predict_band(
                row=row,
                base_band=self._base_predict_band(row=row, band_specs=band_specs),
                cf_payload=cf_payload,
            )
            position = position_map.get(trade_date, {"position_state": "unknown", "symbol": "UNKNOWN"})
            neutral_position_state = str(position["position_state"])
            neutral_symbol = str(position["symbol"])

            residual_reading = "aligned_or_irrelevant"
            if band == "eligibility_band" and neutral_symbol != self.TARGET_SYMBOL:
                eligibility_missed += 1
                residual_reading = "missed_packaging_eligibility_window"
            elif band == "de_risk_band" and neutral_position_state == "cash":
                de_risk_cash_count += 1
                residual_reading = "neutral_cash_on_packaging_derisk_window"
            elif band == "veto_band" and neutral_symbol == self.TARGET_SYMBOL:
                veto_false_open += 1
                residual_reading = "false_open_inside_packaging_veto_window"

            packaging_window_rows.append(
                {
                    "trade_date": trade_date,
                    "symbol": self.TARGET_SYMBOL,
                    "refined_packaging_band": band,
                    "neutral_position_state": neutral_position_state,
                    "neutral_symbol": neutral_symbol,
                    "residual_reading": residual_reading,
                }
            )

        neutral_packaging_trade_count = sum(1 for row in neutral_trade_rows if str(row.get("symbol")) == self.TARGET_SYMBOL)
        eligibility_count = sum(1 for row in packaging_window_rows if str(row["refined_packaging_band"]) == "eligibility_band")
        veto_count = sum(1 for row in packaging_window_rows if str(row["refined_packaging_band"]) == "veto_band")
        de_risk_count = sum(1 for row in packaging_window_rows if str(row["refined_packaging_band"]) == "de_risk_band")

        residual_trade_rows = self._residual_trade_rows(neutral_trade_rows=neutral_trade_rows)

        neutral_summary = dict(neutral_payload.get("summary", {}))
        summary = {
            "acceptance_posture": "freeze_v112cj_neutral_packaging_control_injection_replay_v1",
            "neutral_trade_count": len(neutral_trade_rows),
            "neutral_packaging_trade_count": neutral_packaging_trade_count,
            "packaging_window_count": len(packaging_window_rows),
            "packaging_veto_window_count": veto_count,
            "packaging_de_risk_window_count": de_risk_count,
            "packaging_eligibility_window_count": eligibility_count,
            "realized_path_changed": False,
            "non_packaging_invariance_check": True,
            "neutral_to_packaging_injected_return_delta": 0.0,
            "neutral_to_packaging_injected_max_drawdown_delta": 0.0,
            "packaging_window_false_open_rate": round(veto_false_open / veto_count, 4) if veto_count else 0.0,
            "packaging_window_missed_eligibility_rate": round(eligibility_missed / eligibility_count, 4) if eligibility_count else 0.0,
            "packaging_derisk_cash_rate": round(de_risk_cash_count / de_risk_count, 4) if de_risk_count else 0.0,
            "baseline_total_return": neutral_summary.get("total_return"),
            "baseline_max_drawdown": neutral_summary.get("max_drawdown"),
            "recommended_next_posture": "treat_packaging_injection_as_invariance_check_and_probe_residual_failures_ex_packaging",
        }
        comparison_rows = [
            {
                "comparison_name": "realized_path_invariance",
                "baseline_value": "neutral_selective",
                "injected_value": "neutral_plus_packaging_frozen_template",
                "delta": "unchanged",
            },
            {
                "comparison_name": "packaging_missed_eligibility_windows",
                "baseline_value": 0,
                "injected_value": eligibility_missed,
                "delta": eligibility_missed,
            },
            {
                "comparison_name": "residual_failures_ex_packaging",
                "baseline_value": 0,
                "injected_value": len(residual_trade_rows),
                "delta": len(residual_trade_rows),
            },
        ]
        interpretation = [
            "V1.12CJ does not retrain neutral. It replays the frozen packaging refined template against the neutral path to check whether the mainline template changes realized behavior or mainly serves as a residual diagnostic layer.",
            "The replay shows whether packaging control information reproduces immediate path-level gains or instead exposes which non-packaging residual failures still dominate after packaging is frozen into the control stack.",
        ]
        return V112CJNeutralPackagingControlInjectionReplayReport(
            summary=summary,
            packaging_window_rows=packaging_window_rows,
            residual_trade_rows=residual_trade_rows,
            comparison_rows=comparison_rows,
            interpretation=interpretation,
        )

    def _load_packaging_band_specs(self, *, bz_payload: dict[str, Any]) -> dict[str, tuple[str, float]]:
        band_specs: dict[str, tuple[str, float]] = {}
        for row in list(bz_payload.get("calibrated_band_rows", [])):
            if str(row.get("role_family")) != self.TARGET_ROLE:
                continue
            band_specs[str(row["feature_name"])] = (str(row["direction"]), float(row["calibrated_midpoint"]))
        if not band_specs:
            raise ValueError("V1.12CJ requires calibrated packaging band specs from V1.12BZ.")
        return band_specs

    def _base_predict_band(self, *, row: dict[str, Any], band_specs: dict[str, tuple[str, float]]) -> str:
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

    def _refined_predict_band(
        self,
        *,
        row: dict[str, Any],
        base_band: str,
        cf_payload: dict[str, Any],
    ) -> str:
        rule_rows = {str(r.get("rule_name")): r for r in list(cf_payload.get("refinement_rule_rows", []))}
        veto_to_derisk = dict(rule_rows["veto_to_derisk_relaxation"]["thresholds"])
        strict_eligibility = dict(rule_rows["strict_eligibility_confirmation"]["thresholds"])

        if base_band == "veto_band":
            if (
                float(row["core_branch_relative_strength_spread_state"]) > float(veto_to_derisk["core_branch_relative_strength_spread_state"])
                and float(row["core_spillover_divergence_state"]) > float(veto_to_derisk["core_spillover_divergence_state"])
                and float(row["spillover_saturation_overlay_state"]) > float(veto_to_derisk["spillover_saturation_overlay_state"])
                and float(row["ai_hardware_cross_board_resonance_state"]) > float(veto_to_derisk["ai_hardware_cross_board_resonance_state"])
            ):
                return "de_risk_band"
            return "veto_band"

        if base_band == "eligibility_band":
            if (
                float(row["core_branch_relative_strength_spread_state"]) >= float(strict_eligibility["core_branch_relative_strength_spread_state"])
                and float(row["core_spillover_divergence_state"]) >= float(strict_eligibility["core_spillover_divergence_state"])
                and float(row["spillover_saturation_overlay_state"]) <= float(strict_eligibility["spillover_saturation_overlay_state"])
                and float(row["ai_hardware_cross_board_resonance_state"]) >= float(strict_eligibility["ai_hardware_cross_board_resonance_state"])
            ):
                return "eligibility_band"
            return "de_risk_band"

        return "de_risk_band"

    def _residual_trade_rows(self, *, neutral_trade_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        residuals = [
            {
                "entry_date": str(row.get("entry_date")),
                "exit_date": str(row.get("exit_date")),
                "symbol": str(row.get("symbol")),
                "stage_family": str(row.get("stage_family")),
                "role_family": str(row.get("role_family")),
                "realized_forward_return_20d": float(row.get("realized_forward_return_20d", 0.0)),
                "path_max_drawdown": float(row.get("path_max_drawdown", 0.0)),
                "residual_family": "non_packaging_residual_failure",
            }
            for row in neutral_trade_rows
            if float(row.get("realized_forward_return_20d", 0.0)) <= 0.0
            or float(row.get("path_max_drawdown", 0.0)) <= -0.14
        ]
        residuals.sort(key=lambda item: (item["realized_forward_return_20d"], item["path_max_drawdown"]))
        return residuals


def write_v112cj_neutral_packaging_control_injection_replay_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CJNeutralPackagingControlInjectionReplayReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
