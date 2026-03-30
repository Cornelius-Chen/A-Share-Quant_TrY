from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TOXIC_COMPANION_FAMILY = "entry_suppression_opportunity_cost"


@dataclass(slots=True)
class FactorProtocolRow:
    entry_name: str
    evaluation_bucket: str
    protocol_posture: str
    occurrence_count: int
    report_count: int
    net_family_edge: float
    positive_opportunity_cost: float
    toxic_companion_pocket_count: int
    min_pocket_net_edge: float | None
    rationale: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "entry_name": self.entry_name,
            "evaluation_bucket": self.evaluation_bucket,
            "protocol_posture": self.protocol_posture,
            "occurrence_count": self.occurrence_count,
            "report_count": self.report_count,
            "net_family_edge": self.net_family_edge,
            "positive_opportunity_cost": self.positive_opportunity_cost,
            "toxic_companion_pocket_count": self.toxic_companion_pocket_count,
            "min_pocket_net_edge": self.min_pocket_net_edge,
            "rationale": self.rationale,
        }


@dataclass(slots=True)
class FactorEvaluationProtocolReport:
    summary: dict[str, Any]
    factor_rows: list[FactorProtocolRow]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "factor_rows": [row.as_dict() for row in self.factor_rows],
            "interpretation": self.interpretation,
        }


def load_json_report(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Report at {path} must decode to a mapping.")
    return payload


class FactorEvaluationProtocolAnalyzer:
    """Apply a first-pass formal protocol to current candidate factors."""

    def analyze(
        self,
        *,
        registry_payload: dict[str, Any],
        family_inventory_payload: dict[str, Any],
    ) -> FactorEvaluationProtocolReport:
        registry_rows = registry_payload.get("registry_rows", [])
        family_rows = family_inventory_payload.get("family_rows", [])
        pocket_rows = family_inventory_payload.get("pocket_rows", [])
        if not isinstance(registry_rows, list):
            raise ValueError("Registry payload must contain registry_rows.")
        if not isinstance(family_rows, list):
            raise ValueError("Family inventory payload must contain family_rows.")
        if not isinstance(pocket_rows, list):
            raise ValueError("Family inventory payload must contain pocket_rows.")

        family_by_name = {
            str(row["family_name"]): row for row in family_rows if "family_name" in row
        }
        candidate_entries = [
            row for row in registry_rows if str(row.get("bucket")) == "candidate_factor"
        ]
        factor_rows: list[FactorProtocolRow] = []
        bucket_counts = {
            "evaluate_now": 0,
            "evaluate_with_penalty": 0,
            "hold_for_more_sample": 0,
        }

        for entry in candidate_entries:
            entry_name = str(entry["entry_name"])
            family_row = family_by_name.get(entry_name)
            if family_row is None:
                raise ValueError(f"Missing family inventory row for candidate factor {entry_name}.")

            family_pockets = []
            for pocket in pocket_rows:
                family_counts = pocket.get("family_counts", {})
                if isinstance(family_counts, dict) and entry_name in family_counts:
                    family_pockets.append(pocket)

            toxic_companion_pocket_count = 0
            pocket_net_edges: list[float] = []
            for pocket in family_pockets:
                family_counts = pocket.get("family_counts", {})
                if isinstance(family_counts, dict) and TOXIC_COMPANION_FAMILY in family_counts:
                    toxic_companion_pocket_count += 1
                pocket_net_edges.append(float(pocket.get("net_family_edge", 0.0)))

            occurrence_count = int(family_row.get("occurrence_count", 0))
            report_count = int(family_row.get("report_count", 0))
            net_family_edge = float(family_row.get("net_family_edge", 0.0))
            positive_opportunity_cost = float(family_row.get("positive_opportunity_cost", 0.0))
            min_pocket_net_edge = min(pocket_net_edges) if pocket_net_edges else None

            if (
                occurrence_count >= 2
                and report_count >= 2
                and net_family_edge >= 1000.0
                and positive_opportunity_cost == 0.0
                and toxic_companion_pocket_count == 0
                and (min_pocket_net_edge is None or min_pocket_net_edge > 0.0)
            ):
                evaluation_bucket = "evaluate_now"
                protocol_posture = "promote_into_first_pass_factor_evaluation"
                rationale = (
                    "Repeated clean evidence, positive net edge, and no toxic opportunity-cost companion "
                    "mean this factor is ready for first-pass evaluation now."
                )
            elif (
                occurrence_count >= 2
                and net_family_edge > 0.0
                and (
                    toxic_companion_pocket_count > 0
                    or positive_opportunity_cost > 0.0
                    or (min_pocket_net_edge is not None and min_pocket_net_edge <= 0.0)
                )
            ):
                evaluation_bucket = "evaluate_with_penalty"
                protocol_posture = "evaluate_but_attach_opportunity_cost_penalty"
                rationale = (
                    "The factor repeats and carries positive edge, but at least one pocket ties it to "
                    "toxic opportunity cost or negative pocket-level net edge."
                )
            else:
                evaluation_bucket = "hold_for_more_sample"
                protocol_posture = "preserve_as_candidate_until_more_repeated_evidence_arrives"
                rationale = (
                    "Current evidence is still too thin or too local to justify formal evaluation beyond "
                    "registry preservation."
                )

            factor_rows.append(
                FactorProtocolRow(
                    entry_name=entry_name,
                    evaluation_bucket=evaluation_bucket,
                    protocol_posture=protocol_posture,
                    occurrence_count=occurrence_count,
                    report_count=report_count,
                    net_family_edge=net_family_edge,
                    positive_opportunity_cost=positive_opportunity_cost,
                    toxic_companion_pocket_count=toxic_companion_pocket_count,
                    min_pocket_net_edge=min_pocket_net_edge,
                    rationale=rationale,
                )
            )
            bucket_counts[evaluation_bucket] += 1

        summary = {
            "candidate_factor_count": len(factor_rows),
            "evaluate_now_count": bucket_counts["evaluate_now"],
            "evaluate_with_penalty_count": bucket_counts["evaluate_with_penalty"],
            "hold_for_more_sample_count": bucket_counts["hold_for_more_sample"],
            "first_pass_shortlist": [
                row.entry_name for row in factor_rows if row.evaluation_bucket == "evaluate_now"
            ],
            "penalty_shortlist": [
                row.entry_name
                for row in factor_rows
                if row.evaluation_bucket == "evaluate_with_penalty"
            ],
            "deferred_shortlist": [
                row.entry_name
                for row in factor_rows
                if row.evaluation_bucket == "hold_for_more_sample"
            ],
            "ready_for_first_pass_factor_evaluation": bucket_counts["evaluate_now"] > 0,
        }
        interpretation = [
            "A factor qualifies for first-pass evaluation only when repeated evidence remains clean after pocket-level opportunity-cost checks.",
            "Penalty-track factors should still be evaluated, but only under an explicit opportunity-cost adjustment rather than as clean retained alpha candidates.",
            "Thin factors should stay in the registry until a later batch adds more repeated evidence.",
        ]
        return FactorEvaluationProtocolReport(
            summary=summary,
            factor_rows=factor_rows,
            interpretation=interpretation,
        )


def write_factor_evaluation_protocol_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: FactorEvaluationProtocolReport,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.as_dict(), handle, indent=2, ensure_ascii=False)
    return output_path
