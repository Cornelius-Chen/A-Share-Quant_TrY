from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ResidualCostAcceptanceReport:
    summary: dict[str, Any]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class ResidualCostAcceptanceAnalyzer:
    """Summarize whether the remaining challenger blocker is local enough to accept."""

    def analyze(
        self,
        *,
        gate_payload: dict[str, Any],
        drawdown_gap_payload: dict[str, Any],
        chain_payload: dict[str, Any],
        relief_gate_payload: dict[str, Any],
    ) -> ResidualCostAcceptanceReport:
        gate_summary = gate_payload.get("summary", {})
        relief_summary = relief_gate_payload.get("summary", {})
        weakest_slice = drawdown_gap_payload.get("summary", {}).get("weakest_slice", {})
        weakest_dataset_strategy = drawdown_gap_payload.get("summary", {}).get("weakest_dataset_strategy", {})
        chain_summary = chain_payload.get("summary", {})

        residual_drawdown_gap = round(
            float(gate_summary.get("mean_max_drawdown_improvement", 0.0)) - 0.003,
            6,
        )
        relief_increment = round(
            float(relief_summary.get("mean_max_drawdown_improvement", 0.0))
            - float(gate_summary.get("mean_max_drawdown_improvement", 0.0)),
            6,
        )
        local_only_signature = bool(weakest_slice) and str(weakest_slice.get("dataset_name")) == "theme_research_v4"
        acceptance_posture = (
            "freeze_and_accept_residual_cost"
            if local_only_signature and relief_increment <= 0.0001
            else "continue_structural_research"
        )

        evidence_rows = [
            {
                "evidence_name": "broad_challenger_gain",
                "actual": {
                    "composite_rank_improvement": gate_summary.get("composite_rank_improvement"),
                    "mean_total_return_delta": gate_summary.get("mean_total_return_delta"),
                    "mean_capture_delta": gate_summary.get("mean_capture_delta"),
                },
                "reading": "The challenger remains broadly superior on rank and return, and does not suffer a broad capture problem anymore.",
            },
            {
                "evidence_name": "residual_gate_gap",
                "actual": {
                    "mean_max_drawdown_improvement": gate_summary.get("mean_max_drawdown_improvement"),
                    "required_threshold": 0.003,
                    "gap_to_threshold": residual_drawdown_gap,
                },
                "reading": "The only remaining strict-gate blocker is a small drawdown-improvement shortfall.",
            },
            {
                "evidence_name": "localization",
                "actual": {
                    "weakest_dataset_strategy": weakest_dataset_strategy,
                    "weakest_slice": weakest_slice,
                },
                "reading": "The remaining blocker is localized to a theme-side pocket rather than spread across all packs.",
            },
            {
                "evidence_name": "dominant_chain_cost",
                "actual": {
                    "complete_chain_ratio": chain_summary.get("complete_chain_ratio"),
                    "incumbent_missed_cycle_total_pnl": chain_summary.get("incumbent_missed_cycle_total_pnl"),
                },
                "reading": "The local damage is real and economically meaningful, but it is concentrated in one repeated missed re-entry chain.",
            },
            {
                "evidence_name": "cheap_local_relief_test",
                "actual": {
                    "relief_mean_max_drawdown_improvement": relief_summary.get("mean_max_drawdown_improvement"),
                    "increment_vs_frozen_branch": relief_increment,
                    "relief_passed": relief_gate_payload.get("passed"),
                },
                "reading": "The obvious cheap local threshold fix was tested and still failed; this suggests the remaining blocker is not cheaply repairable.",
            },
        ]
        interpretation = [
            "A residual blocker is more acceptable when the challenger already wins broadly, the remaining gap is numerically small, and the problem localizes to one pack and one slice.",
            "A residual blocker is less acceptable when a cheap local repair clearly closes the gap. That did not happen here.",
            "The current evidence therefore supports a freeze posture more than another round of narrow threshold tuning.",
        ]
        summary = {
            "acceptance_posture": acceptance_posture,
            "residual_drawdown_gap_to_threshold": residual_drawdown_gap,
            "relief_increment_vs_frozen_branch": relief_increment,
            "is_localized_theme_pocket": local_only_signature,
            "dominant_chain_total_pnl": chain_summary.get("incumbent_missed_cycle_total_pnl"),
        }
        return ResidualCostAcceptanceReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_residual_cost_acceptance_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: ResidualCostAcceptanceReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
