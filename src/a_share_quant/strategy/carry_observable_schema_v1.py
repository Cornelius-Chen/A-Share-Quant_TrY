from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CarryObservableSchemaReport:
    summary: dict[str, Any]
    schema_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "schema_rows": self.schema_rows,
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class CarryObservableSchemaAnalyzer:
    """Define the first row-isolated observable schema for carry-in-basis rows."""

    def analyze(
        self,
        *,
        design_payload: dict[str, Any],
        mechanism_b_payload: dict[str, Any],
        mechanism_c_payload: dict[str, Any],
    ) -> CarryObservableSchemaReport:
        design_summary = dict(design_payload.get("summary", {}))
        if not bool(design_summary.get("do_open_carry_factor_design")):
            raise ValueError("Carry factor design must be open before defining the schema.")
        if not bool(design_summary.get("row_isolation_required")):
            raise ValueError("Carry schema v1 requires row-isolated design posture.")

        def extract_carry_row(payload: dict[str, Any], strategy_name: str) -> dict[str, Any]:
            mechanism_rows = payload.get("mechanism_rows", [])
            if not isinstance(mechanism_rows, list):
                raise ValueError("Mechanism payload must contain mechanism_rows.")
            for row in mechanism_rows:
                if str(row.get("mechanism_type")) != "carry_in_basis_advantage":
                    continue
                incumbent_cycle = dict(row.get("incumbent_cycle", {}))
                challenger_cycle = dict(row.get("closest_challenger_cycle", {}))
                if not incumbent_cycle or not challenger_cycle:
                    raise ValueError("Carry row must contain incumbent and challenger cycles.")
                incumbent_entry_price = float(incumbent_cycle["entry_price"])
                incumbent_exit_price = float(incumbent_cycle["exit_price"])
                challenger_entry_price = float(challenger_cycle["entry_price"])
                challenger_exit_price = float(challenger_cycle["exit_price"])
                basis_advantage_abs = round(incumbent_entry_price - challenger_entry_price, 6)
                basis_advantage_bps = round(
                    basis_advantage_abs / incumbent_entry_price * 10000.0, 4
                )
                challenger_carry_days = int(challenger_cycle["holding_days"]) - int(
                    incumbent_cycle["holding_days"]
                )
                same_exit_date = str(challenger_cycle["exit_date"]) == str(
                    incumbent_cycle["exit_date"]
                )
                return {
                    "strategy_name": strategy_name,
                    "trigger_date": str(row.get("trigger_date")),
                    "incumbent_entry_date": str(incumbent_cycle["entry_date"]),
                    "incumbent_exit_date": str(incumbent_cycle["exit_date"]),
                    "challenger_entry_date": str(challenger_cycle["entry_date"]),
                    "challenger_exit_date": str(challenger_cycle["exit_date"]),
                    "basis_advantage_abs": basis_advantage_abs,
                    "basis_advantage_bps": basis_advantage_bps,
                    "challenger_carry_days": challenger_carry_days,
                    "same_exit_date": same_exit_date,
                    "pnl_delta_vs_closest": float(row.get("pnl_delta_vs_closest", 0.0)),
                    "observable_mode": "negative_cycle_basis_row",
                }
            raise ValueError(f"Missing carry_in_basis_advantage row for {strategy_name}.")

        schema_rows = [
            extract_carry_row(mechanism_b_payload, "mainline_trend_b"),
            extract_carry_row(mechanism_c_payload, "mainline_trend_c"),
        ]

        basis_bps_values = [float(row["basis_advantage_bps"]) for row in schema_rows]
        carry_days_values = [int(row["challenger_carry_days"]) for row in schema_rows]
        same_exit_count = sum(1 for row in schema_rows if bool(row["same_exit_date"]))
        summary = {
            "schema_posture": "open_carry_observable_schema_v1",
            "schema_row_count": len(schema_rows),
            "observable_mode": "negative_cycle_basis_row",
            "required_fields": [
                "basis_advantage_abs",
                "basis_advantage_bps",
                "challenger_carry_days",
                "same_exit_date",
                "pnl_delta_vs_closest",
            ],
            "mean_basis_advantage_bps": round(sum(basis_bps_values) / len(basis_bps_values), 4),
            "common_carry_days": min(carry_days_values) == max(carry_days_values),
            "same_exit_consistency": same_exit_count == len(schema_rows),
            "allow_scoring_design_next": True,
        }
        interpretation = [
            "Carry schema v1 is row-level and negative-cycle specific: it isolates the better-basis challenger row instead of inheriting the whole mixed pocket.",
            "The core observables are basis advantage, carry duration, same-exit alignment, and realized pnl delta against the incumbent cycle.",
            "Once this schema is explicit, the next factor step can design scoring or filtering around carry rows rather than around the entire pocket.",
        ]
        return CarryObservableSchemaReport(
            summary=summary,
            schema_rows=schema_rows,
            interpretation=interpretation,
        )


def write_carry_observable_schema_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CarryObservableSchemaReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
