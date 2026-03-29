from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class DamageTransitionReport:
    summary: dict[str, Any]
    symbol_cases: list[dict[str, Any]]
    transition_patterns: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "symbol_cases": self.symbol_cases,
            "transition_patterns": self.transition_patterns,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class DamageTransitionAnalyzer:
    """Summarize when repeated path shifts turn into real trade damage."""

    def analyze(self, *, case_payloads: list[dict[str, Any]]) -> DamageTransitionReport:
        symbol_cases = [self._analyze_case(case) for case in case_payloads]
        transition_patterns = self._build_transition_patterns(symbol_cases)
        damage_cases = [case for case in symbol_cases if case["case_class"] == "damage_case"]
        summary = {
            "case_count": len(symbol_cases),
            "damage_case_count": len(damage_cases),
            "damage_case_symbols": [case["symbol"] for case in damage_cases],
            "latent_case_symbols": [
                case["symbol"] for case in symbol_cases if case["case_class"] != "damage_case"
            ],
            "core_rule": (
                "Repeated approval/permission or assignment splits become promotion-relevant "
                "only when they also change emitted actions or active-position state."
            ),
        }
        interpretation = [
            "Repeated path-shift dates alone are not enough; the key question is whether they alter fills, trades, or realized pnl.",
            "Approval-sector and permission splits often appear before damage, but they can remain economically silent if both candidates keep the same executed trade path.",
            "The first real damage case is the one where repeated path shifts cross an active tradable boundary and force a different action sequence.",
        ]
        return DamageTransitionReport(
            summary=summary,
            symbol_cases=symbol_cases,
            transition_patterns=transition_patterns,
            interpretation=interpretation,
        )

    def _analyze_case(self, case: dict[str, Any]) -> dict[str, Any]:
        symbol = str(case["symbol"])
        timeline_payload = case["timeline_payload"]
        path_payload = case["path_payload"]

        comparison_records = timeline_payload.get("comparison_records", [])
        repeated_shift_dates = path_payload.get("repeated_shift_dates", [])
        detailed_shifts = path_payload.get("detailed_shifts", [])

        pnl_deltas = [float(item.get("pnl_delta", 0.0)) for item in comparison_records]
        fill_deltas = [
            int(item.get("challenger_fill_count", 0)) - int(item.get("incumbent_fill_count", 0))
            for item in comparison_records
        ]
        trade_deltas = [
            int(item.get("challenger_trade_count", 0)) - int(item.get("incumbent_trade_count", 0))
            for item in comparison_records
        ]
        repeated_dates = {str(item["trade_date"]) for item in repeated_shift_dates}
        repeated_details = [
            item for item in detailed_shifts if str(item.get("trade_date")) in repeated_dates
        ]
        difference_types = sorted(
            {
                diff
                for item in repeated_details
                for diff in item.get("difference_types", [])
            }
        )
        has_permission_split = "permission" in difference_types
        has_approved_sector_split = "approved_sector" in difference_types
        has_assignment_split = "assignment_layer" in difference_types
        has_action_shift = any(
            diff in difference_types for diff in ("emitted_actions", "position_qty", "pending_buy", "pending_sell")
        )
        has_exit_shift = "exit_reason" in difference_types
        has_trade_damage = any(abs(delta) > 1e-9 for delta in pnl_deltas)
        has_trade_path_change = has_trade_damage or any(delta != 0 for delta in fill_deltas + trade_deltas)

        if has_trade_damage:
            case_class = "damage_case"
        elif has_assignment_split and has_permission_split:
            case_class = "latent_assignment_permission_case"
        elif has_approved_sector_split and has_permission_split:
            case_class = "latent_approval_permission_case"
        else:
            case_class = "latent_path_shift_case"

        return {
            "symbol": symbol,
            "case_class": case_class,
            "repeated_shift_dates": sorted(repeated_dates),
            "difference_types": difference_types,
            "has_permission_split": has_permission_split,
            "has_approved_sector_split": has_approved_sector_split,
            "has_assignment_split": has_assignment_split,
            "has_action_shift": has_action_shift,
            "has_exit_shift": has_exit_shift,
            "has_trade_path_change": has_trade_path_change,
            "has_trade_damage": has_trade_damage,
            "max_abs_pnl_delta": max((abs(delta) for delta in pnl_deltas), default=0.0),
            "comparison_overview": comparison_records,
        }

    def _build_transition_patterns(self, symbol_cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
        patterns: list[dict[str, Any]] = []
        for case in symbol_cases:
            if case["case_class"] == "damage_case":
                patterns.append(
                    {
                        "pattern_name": f"{case['symbol']}_damage_transition",
                        "symbol": case["symbol"],
                        "rule": (
                            "Repeated approval/permission or assignment splits become real damage "
                            "when they coincide with action-state divergence."
                        ),
                        "evidence": {
                            "difference_types": case["difference_types"],
                            "repeated_shift_dates": case["repeated_shift_dates"],
                            "max_abs_pnl_delta": case["max_abs_pnl_delta"],
                        },
                    }
                )
            else:
                patterns.append(
                    {
                        "pattern_name": f"{case['symbol']}_latent_transition",
                        "symbol": case["symbol"],
                        "rule": (
                            "Repeated path-shift dates can remain latent if they do not alter the executed trade path."
                        ),
                        "evidence": {
                            "difference_types": case["difference_types"],
                            "repeated_shift_dates": case["repeated_shift_dates"],
                            "max_abs_pnl_delta": case["max_abs_pnl_delta"],
                        },
                    }
                )
        return patterns


def write_damage_transition_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: DamageTransitionReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
