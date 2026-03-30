from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CarryScoringDesignReport:
    summary: dict[str, Any]
    score_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "score_rows": self.score_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class CarryScoringDesignAnalyzer:
    """Define the first bounded scoring design for the carry observable schema."""

    BASIS_WEIGHT = 0.45
    EXIT_ALIGNMENT_WEIGHT = 0.2
    CARRY_DURATION_WEIGHT = 0.15
    REALIZED_CONFIRMATION_WEIGHT = 0.2

    def analyze(self, *, schema_payload: dict[str, Any]) -> CarryScoringDesignReport:
        summary = dict(schema_payload.get("summary", {}))
        schema_rows = schema_payload.get("schema_rows", [])
        if not bool(summary.get("allow_scoring_design_next")):
            raise ValueError("Carry scoring design requires an open schema-to-scoring transition.")
        if not isinstance(schema_rows, list) or not schema_rows:
            raise ValueError("Carry schema payload must contain schema_rows.")

        score_rows: list[dict[str, Any]] = []
        for row in schema_rows:
            basis_advantage_bps = float(row["basis_advantage_bps"])
            same_exit_date = bool(row["same_exit_date"])
            challenger_carry_days = int(row["challenger_carry_days"])
            pnl_delta_vs_closest = float(row["pnl_delta_vs_closest"])

            basis_component = min(max(basis_advantage_bps / 250.0, 0.0), 1.0)
            exit_alignment_component = 1.0 if same_exit_date else 0.0
            carry_duration_component = 1.0 if challenger_carry_days >= 1 else 0.0
            realized_confirmation_component = min(max(pnl_delta_vs_closest / 800.0, 0.0), 1.0)

            carry_score = round(
                self.BASIS_WEIGHT * basis_component
                + self.EXIT_ALIGNMENT_WEIGHT * exit_alignment_component
                + self.CARRY_DURATION_WEIGHT * carry_duration_component
                + self.REALIZED_CONFIRMATION_WEIGHT * realized_confirmation_component,
                6,
            )
            score_rows.append(
                {
                    "strategy_name": str(row["strategy_name"]),
                    "basis_component": round(basis_component, 6),
                    "exit_alignment_component": round(exit_alignment_component, 6),
                    "carry_duration_component": round(carry_duration_component, 6),
                    "realized_confirmation_component": round(realized_confirmation_component, 6),
                    "carry_score_v1": carry_score,
                    "score_formula": (
                        "0.45*basis + 0.20*same_exit + 0.15*carry_days + 0.20*realized_confirmation"
                    ),
                }
            )

        carry_scores = [float(row["carry_score_v1"]) for row in score_rows]
        design_summary = {
            "design_posture": "open_carry_scoring_design_v1",
            "score_row_count": len(score_rows),
            "score_field_name": "carry_score_v1",
            "score_formula": "0.45*basis + 0.20*same_exit + 0.15*carry_days + 0.20*realized_confirmation",
            "min_score": round(min(carry_scores), 6),
            "max_score": round(max(carry_scores), 6),
            "mean_score": round(sum(carry_scores) / len(carry_scores), 6),
            "allow_factor_pilot_next": True,
            "allow_strategy_integration_now": False,
            "allow_retained_feature_promotion_now": False,
        }
        interpretation = [
            "Carry scoring design v1 stays inside the row-isolated boundary and scores only row-level carry observables.",
            "The score combines basis advantage, same-exit alignment, positive carry duration, and realized negative-cycle confirmation.",
            "This opens a bounded factor pilot next, but it still keeps strategy integration and retained-feature promotion off.",
        ]
        return CarryScoringDesignReport(
            summary=design_summary,
            score_rows=score_rows,
            interpretation=interpretation,
        )


def write_carry_scoring_design_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CarryScoringDesignReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
