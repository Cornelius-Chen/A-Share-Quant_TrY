from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CarryInBasisFirstPassReport:
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


class CarryInBasisFirstPassAnalyzer:
    """Decide whether carry-in-basis advantage deserves a bounded first-pass factor lane."""

    def analyze(
        self,
        *,
        protocol_payload: dict[str, Any],
        family_inventory_payload: dict[str, Any],
        cross_strategy_payload: dict[str, Any],
        mechanism_b_payload: dict[str, Any],
        mechanism_c_payload: dict[str, Any],
    ) -> CarryInBasisFirstPassReport:
        factor_rows = {
            str(row["entry_name"]): row for row in protocol_payload.get("factor_rows", [])
        }
        carry_protocol = factor_rows.get("carry_in_basis_advantage")
        if carry_protocol is None:
            raise ValueError("Protocol payload must contain carry_in_basis_advantage.")

        family_rows = {
            str(row["family_name"]): row for row in family_inventory_payload.get("family_rows", [])
        }
        carry_family = family_rows.get("carry_in_basis_advantage")
        if carry_family is None:
            raise ValueError("Family inventory payload must contain carry_in_basis_advantage.")

        shared_mechanisms = cross_strategy_payload.get("shared_mechanisms", [])
        if not isinstance(shared_mechanisms, list):
            raise ValueError("Cross-strategy payload must contain shared_mechanisms.")
        shared_carry = any(
            str(row.get("mechanism_type")) == "carry_in_basis_advantage"
            and int(row.get("shared_strategy_count", 0)) >= 2
            for row in shared_mechanisms
        )

        def contains_carry(payload: dict[str, Any]) -> bool:
            rows = payload.get("mechanism_rows", [])
            if not isinstance(rows, list):
                raise ValueError("Mechanism payload must contain mechanism_rows.")
            return any(
                str(row.get("mechanism_type")) == "carry_in_basis_advantage"
                and str(row.get("cycle_sign")) == "negative"
                for row in rows
            )

        b_contains = contains_carry(mechanism_b_payload)
        c_contains = contains_carry(mechanism_c_payload)

        evaluate_now = str(carry_protocol.get("evaluation_bucket")) == "evaluate_now"
        repeated_clean_evidence = (
            int(carry_family.get("occurrence_count", 0)) >= 2
            and int(carry_family.get("report_count", 0)) >= 2
            and float(carry_family.get("positive_opportunity_cost", 0.0)) == 0.0
            and float(carry_family.get("net_family_edge", 0.0)) > 0.0
        )
        bounded_first_pass_ready = (
            evaluate_now and repeated_clean_evidence and shared_carry and b_contains and c_contains
        )

        acceptance_posture = (
            "open_carry_in_basis_first_pass_as_bounded_factor_candidate"
            if bounded_first_pass_ready
            else "hold_carry_in_basis_before_factor_design"
        )
        summary = {
            "acceptance_posture": acceptance_posture,
            "evaluate_now": evaluate_now,
            "repeated_clean_evidence": repeated_clean_evidence,
            "cross_strategy_reuse_confirmed": shared_carry,
            "mechanism_present_in_b": b_contains,
            "mechanism_present_in_c": c_contains,
            "do_open_bounded_carry_factor_lane": bounded_first_pass_ready,
            "promote_to_retained_feature_now": False,
        }
        evidence_rows = [
            {
                "evidence_name": "protocol_bucket",
                "actual": {
                    "evaluation_bucket": carry_protocol.get("evaluation_bucket"),
                    "protocol_posture": carry_protocol.get("protocol_posture"),
                },
                "reading": "The factor must first clear protocol-level readiness before any bounded design work should open.",
            },
            {
                "evidence_name": "family_inventory_cleanliness",
                "actual": {
                    "occurrence_count": carry_family.get("occurrence_count"),
                    "report_count": carry_family.get("report_count"),
                    "net_family_edge": carry_family.get("net_family_edge"),
                    "positive_opportunity_cost": carry_family.get("positive_opportunity_cost"),
                },
                "reading": "A first-pass lane should only open when repeated evidence remains net-positive without opportunity-cost contamination.",
            },
            {
                "evidence_name": "cross_strategy_reuse",
                "actual": {
                    "shared_carry": shared_carry,
                    "cross_strategy_summary": cross_strategy_payload.get("summary", {}),
                    "mechanism_present_in_b": b_contains,
                    "mechanism_present_in_c": c_contains,
                },
                "reading": "The first bounded factor lane should prefer candidate structures that repeat across B/C rather than one-off strategy accidents.",
            },
        ]
        interpretation = [
            "A bounded first-pass factor lane is narrower than retained-feature promotion: it opens design work without claiming full structural closure.",
            "Carry-in-basis advantage clears that bar when the protocol bucket is evaluate-now, the family remains clean, and the mechanism repeats across B/C.",
            "So the correct next move is to open a bounded carry factor lane, while still keeping retained-feature promotion closed for now.",
        ]
        return CarryInBasisFirstPassReport(
            summary=summary,
            evidence_rows=evidence_rows,
            interpretation=interpretation,
        )


def write_carry_in_basis_first_pass_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: CarryInBasisFirstPassReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
