from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V112CLCoreResidualControlProbeReviewReport:
    summary: dict[str, Any]
    family_rows: list[dict[str, Any]]
    evidence_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "family_rows": self.family_rows,
            "evidence_rows": self.evidence_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class V112CLCoreResidualControlProbeReviewAnalyzer:
    def analyze(
        self,
        *,
        ck_payload: dict[str, Any],
        bh_payload: dict[str, Any],
        bk_payload: dict[str, Any],
    ) -> V112CLCoreResidualControlProbeReviewReport:
        residual_rows = list(ck_payload.get("residual_rows", []))
        neutral_trade_rows = list(bh_payload.get("trade_rows", []))
        bk_trade_rows = list(bk_payload.get("trade_rows", []))

        neutral_by_symbol = {}
        for row in neutral_trade_rows:
            neutral_by_symbol.setdefault(str(row.get("symbol")), []).append(row)

        family_rows: list[dict[str, Any]] = []
        evidence_rows: list[dict[str, Any]] = []

        core_rows = [row for row in residual_rows if str(row.get("residual_family")) == "core_module_leader_mature_markup_overstay"]
        if core_rows:
            neutral_core = neutral_by_symbol.get("300308", [])
            family_rows.append(
                {
                    "residual_family": "core_module_leader_mature_markup_overstay",
                    "candidate_control_action": "holding_veto_or_shorter_half_life",
                    "control_reading": "late main_markup continuation should not be treated as plain eligibility once maturity weakens and drawdown tolerance deteriorates",
                    "sample_count": len(core_rows),
                    "next_probe": "core_leader_holding_veto_probe",
                }
            )
            for row in neutral_core:
                evidence_rows.append(
                    {
                        "residual_family": "core_module_leader_mature_markup_overstay",
                        "symbol": "300308",
                        "entry_date": str(row.get("entry_date")),
                        "realized_forward_return_20d": float(row.get("realized_forward_return_20d", 0.0)),
                        "path_max_drawdown": float(row.get("path_max_drawdown", 0.0)),
                        "predicted_winner_prob": float(row.get("predicted_winner_prob", 0.0)),
                        "probability_margin": float(row.get("probability_margin", 0.0)),
                        "selective_score": float(row.get("selective_score", 0.0)),
                        "evidence_reading": "bad_window" if float(row.get("realized_forward_return_20d", 0.0)) < 0.0 else "reference_window",
                    }
                )

        high_beta_rows = [row for row in residual_rows if str(row.get("residual_family")) == "high_beta_core_module_expression_risk"]
        if high_beta_rows:
            family_rows.append(
                {
                    "residual_family": "high_beta_core_module_expression_risk",
                    "candidate_control_action": "de_risk_not_entry_veto",
                    "control_reading": "high-beta core expression still carries alpha; the issue is drawdown tolerance and expression size rather than outright disqualification",
                    "sample_count": len(high_beta_rows),
                    "next_probe": "high_beta_core_derisk_probe",
                }
            )
            for row in [r for r in bk_trade_rows if str(r.get("symbol")) == "300502"]:
                evidence_rows.append(
                    {
                        "residual_family": "high_beta_core_module_expression_risk",
                        "symbol": "300502",
                        "entry_date": str(row.get("entry_date")),
                        "stage_family": str(row.get("stage_family")),
                        "realized_forward_return_20d": float(row.get("realized_forward_return_20d", 0.0)),
                        "path_max_drawdown": float(row.get("path_max_drawdown", 0.0)),
                        "evidence_reading": "high_drawdown_reference"
                        if float(row.get("path_max_drawdown", 0.0)) <= -0.15
                        else "manageable_expression_reference",
                    }
                )

        summary = {
            "acceptance_posture": "freeze_v112cl_core_residual_control_probe_review_v1",
            "family_count": len(family_rows),
            "dominant_control_split": "core_leader_to_holding_veto__high_beta_core_to_derisk",
            "packaging_template_kept_frozen": True,
            "recommended_next_posture": "open_core_leader_holding_veto_probe_and_high_beta_core_derisk_probe",
        }
        interpretation = [
            "V1.12CL translates ex-packaging residual families into action-type hypotheses rather than reopening blanket gate search.",
            "The review indicates that core-leader residuals look like mature-markup overstay problems, while high-beta core residuals look like expression-risk problems that should be handled by de-risk rather than by outright veto.",
        ]
        return V112CLCoreResidualControlProbeReviewReport(
            summary=summary,
            family_rows=family_rows,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_v112cl_core_residual_control_probe_review_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V112CLCoreResidualControlProbeReviewReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
