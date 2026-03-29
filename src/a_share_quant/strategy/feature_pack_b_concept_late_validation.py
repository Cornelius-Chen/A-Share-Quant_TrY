from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FeaturePackBConceptLateValidationReport:
    summary: dict[str, Any]
    variant_rows: list[dict[str, Any]]
    trigger_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "variant_rows": self.variant_rows,
            "trigger_rows": self.trigger_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


def _candidate_record(payload: dict[str, Any], candidate_name: str) -> dict[str, Any]:
    for record in payload.get("candidate_records", []):
        if str(record.get("candidate_name")) == candidate_name:
            return record
    raise ValueError(f"Candidate {candidate_name!r} not found in payload.")


def _daily_record_map(candidate_record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(record["trade_date"]): record
        for record in candidate_record.get("daily_records", [])
    }


def _total_pnl(candidate_record: dict[str, Any]) -> float:
    return round(
        sum(float(trade.get("pnl", 0.0)) for trade in candidate_record.get("closed_trades", [])),
        6,
    )


class FeaturePackBConceptLateValidationAnalyzer:
    """Decide whether the concept-to-late track still merits more budget."""

    def analyze(
        self,
        *,
        bridge_payload: dict[str, Any],
        baseline_payload: dict[str, Any],
        baseline_challenger_name: str,
        variant_payloads: list[tuple[str, dict[str, Any], str]],
    ) -> FeaturePackBConceptLateValidationReport:
        trigger_dates = [str(row["trigger_date"]) for row in bridge_payload.get("bridge_rows", [])]
        trigger_count = len(trigger_dates)

        incumbent_name = "shared_default"
        baseline_incumbent = _candidate_record(baseline_payload, incumbent_name)
        baseline_challenger = _candidate_record(baseline_payload, baseline_challenger_name)
        baseline_delta = round(_total_pnl(baseline_challenger) - _total_pnl(baseline_incumbent), 6)
        baseline_trade_count = len(baseline_challenger.get("closed_trades", []))
        baseline_fill_count = len(baseline_challenger.get("fills", []))

        variant_rows: list[dict[str, Any]] = []
        trigger_rows: list[dict[str, Any]] = []

        baseline_daily_map = _daily_record_map(baseline_challenger)
        for trigger_date in trigger_dates:
            baseline_record = baseline_daily_map.get(trigger_date, {})
            trigger_rows.append(
                {
                    "trigger_date": trigger_date,
                    "baseline_assignment_layer": baseline_record.get("assignment_layer"),
                    "baseline_assignment_reason": baseline_record.get("assignment_reason"),
                    "baseline_emitted_actions": list(baseline_record.get("emitted_actions", [])),
                }
            )

        for variant_name, payload, challenger_name in variant_payloads:
            incumbent_record = _candidate_record(payload, incumbent_name)
            challenger_record = _candidate_record(payload, challenger_name)
            challenger_daily_map = _daily_record_map(challenger_record)
            repaired_trigger_dates: list[str] = []
            repaired_buy_dates: list[str] = []

            for trigger_row in trigger_rows:
                trigger_date = str(trigger_row["trigger_date"])
                daily_record = challenger_daily_map.get(trigger_date, {})
                assignment_layer = str(daily_record.get("assignment_layer", ""))
                emitted_actions = [str(action) for action in daily_record.get("emitted_actions", [])]
                if assignment_layer == "late_mover":
                    repaired_trigger_dates.append(trigger_date)
                if "buy" in emitted_actions:
                    repaired_buy_dates.append(trigger_date)
                trigger_row[f"{variant_name}_assignment_layer"] = assignment_layer or None
                trigger_row[f"{variant_name}_assignment_reason"] = daily_record.get("assignment_reason")
                trigger_row[f"{variant_name}_emitted_actions"] = emitted_actions

            incumbent_total_pnl = _total_pnl(incumbent_record)
            challenger_total_pnl = _total_pnl(challenger_record)
            pnl_delta = round(challenger_total_pnl - incumbent_total_pnl, 6)
            alpha_retention_ratio = round(pnl_delta / baseline_delta, 6) if baseline_delta else None

            variant_rows.append(
                {
                    "variant_name": variant_name,
                    "challenger_name": challenger_name,
                    "incumbent_total_pnl": incumbent_total_pnl,
                    "challenger_total_pnl": challenger_total_pnl,
                    "pnl_delta": pnl_delta,
                    "alpha_retention_ratio_vs_baseline": alpha_retention_ratio,
                    "challenger_trade_count": len(challenger_record.get("closed_trades", [])),
                    "challenger_fill_count": len(challenger_record.get("fills", [])),
                    "extra_trade_count_vs_baseline": len(challenger_record.get("closed_trades", []))
                    - baseline_trade_count,
                    "extra_fill_count_vs_baseline": len(challenger_record.get("fills", []))
                    - baseline_fill_count,
                    "repaired_trigger_dates": repaired_trigger_dates,
                    "repaired_buy_dates": repaired_buy_dates,
                    "repaired_trigger_count": len(repaired_trigger_dates),
                    "repair_completion_ratio": round(len(repaired_trigger_dates) / trigger_count, 6)
                    if trigger_count
                    else 0.0,
                }
            )

        variant_rows.sort(key=lambda row: float(row["pnl_delta"]), reverse=True)
        best_variant = variant_rows[0] if variant_rows else None
        max_retention_ratio = (
            max(float(row["alpha_retention_ratio_vs_baseline"]) for row in variant_rows)
            if variant_rows and baseline_delta
            else 0.0
        )
        max_repaired_trigger_count = (
            max(int(row["repaired_trigger_count"]) for row in variant_rows) if variant_rows else 0
        )
        acceptance_posture = (
            "close_track_b_as_negative_informative"
            if best_variant is not None
            and max_retention_ratio < 0.5
            and max_repaired_trigger_count < trigger_count
            else "continue_hyper_local_refinement"
        )

        summary = {
            "case_name": bridge_payload.get("summary", {}).get("case_name"),
            "baseline_variant_name": "v1_control",
            "baseline_challenger_name": baseline_challenger_name,
            "baseline_pnl_delta": baseline_delta,
            "bridge_trigger_count": trigger_count,
            "best_variant_name": best_variant.get("variant_name") if best_variant else None,
            "best_variant_pnl_delta": best_variant.get("pnl_delta") if best_variant else None,
            "best_variant_alpha_retention_ratio": best_variant.get("alpha_retention_ratio_vs_baseline")
            if best_variant
            else None,
            "best_variant_repair_completion_ratio": best_variant.get("repair_completion_ratio")
            if best_variant
            else None,
            "all_tested_variants_degrade_alpha": bool(best_variant and best_variant["pnl_delta"] < baseline_delta),
            "all_tested_variants_remain_partial": max_repaired_trigger_count < trigger_count,
            "acceptance_posture": acceptance_posture,
        }
        interpretation = [
            "Track B should only stay open if concept-to-late variants preserve a meaningful share of the incumbent-relative alpha while also repairing the targeted trigger rows.",
            "Here the tested variants repaired only one of the two bridge rows, and the best alpha-retention ratio stayed well below a durable threshold.",
            "That is strong evidence for an explanatory-but-not-promotable conclusion, not for another round of broad concept-to-late widening.",
        ]
        return FeaturePackBConceptLateValidationReport(
            summary=summary,
            variant_rows=variant_rows,
            trigger_rows=trigger_rows,
            interpretation=interpretation,
        )


def write_feature_pack_b_concept_late_validation_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FeaturePackBConceptLateValidationReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
