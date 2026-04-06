from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JOCommercialAerospaceDecisiveEventRegistryExpansionUtilityAuditV1Report:
    summary: dict[str, Any]
    utility_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "utility_rows": self.utility_rows,
            "interpretation": self.interpretation,
        }


class V134JOCommercialAerospaceDecisiveEventRegistryExpansionUtilityAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.applicability_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134jm_commercial_aerospace_broader_attention_source_applicability_audit_v1.json"
        )
        self.decisive_registry_path = (
            repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_decisive_event_registry_v1.csv"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_decisive_event_registry_expansion_utility_v1.csv"
        )

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def _classify_utility(row: dict[str, str]) -> str:
        reason = row["decisive_reason"]
        semantic = row["decisive_semantic"]
        if reason in {"capital_mapping_with_real_board_implication", "capital_mapping_anchor"}:
            return "broader_symbol_pool_expander"
        if reason in {"decisive_turning_point_risk", "sentiment_transition_anchor"} or semantic == "turning_point_watch":
            return "heat_axis_and_counterpanel_expander"
        if reason == "supply_chain_validation":
            return "carrier_follow_search_expander"
        if reason in {"launch_or_deployment_anchor", "general_context_but_industry_specific"}:
            return "event_context_alignment_expander"
        if reason == "regulatory_or_financing_constraint_anchor":
            return "risk_constraint_anchor_expander"
        return "unclassified_retained_expander"

    def analyze(self) -> V134JOCommercialAerospaceDecisiveEventRegistryExpansionUtilityAuditV1Report:
        applicability = self._load_json(self.applicability_path)
        decisive_rows = self._load_csv(self.decisive_registry_path)
        retained_rows = [row for row in decisive_rows if row["decisive_retained"] == "True"]

        utility_rows: list[dict[str, Any]] = []
        utility_counts: dict[str, int] = {}
        for row in retained_rows:
            utility_class = self._classify_utility(row)
            utility_counts[utility_class] = utility_counts.get(utility_class, 0) + 1
            utility_rows.append(
                {
                    "registry_id": row["registry_id"],
                    "layer": row["layer"],
                    "decisive_semantic": row["decisive_semantic"],
                    "decisive_reason": row["decisive_reason"],
                    "extracted_candidate_count": row["extracted_candidate_count"],
                    "utility_class": utility_class,
                    "source_name": row["source_name"],
                }
            )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(utility_rows[0].keys()))
            writer.writeheader()
            writer.writerows(utility_rows)

        summary = {
            "acceptance_posture": "freeze_v134jo_commercial_aerospace_decisive_event_registry_expansion_utility_audit_v1",
            "same_plane_ready_source_count": applicability["summary"]["same_plane_ready_source_count"],
            "retained_registry_row_count": len(retained_rows),
            "broader_symbol_pool_expander_count": utility_counts.get("broader_symbol_pool_expander", 0),
            "heat_axis_and_counterpanel_expander_count": utility_counts.get("heat_axis_and_counterpanel_expander", 0),
            "carrier_follow_search_expander_count": utility_counts.get("carrier_follow_search_expander", 0),
            "event_context_alignment_expander_count": utility_counts.get("event_context_alignment_expander", 0),
            "risk_constraint_anchor_expander_count": utility_counts.get("risk_constraint_anchor_expander", 0),
            "utility_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_decisive_event_registry_expansion_utility_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34JO is the first real expansion audit under the broader-attention-evidence frontier.",
            "It does not yet promote symbols. It first separates the retained 2026-aligned event registry into utility classes so that broader expansion can proceed by evidence role instead of by vague event importance.",
        ]
        return V134JOCommercialAerospaceDecisiveEventRegistryExpansionUtilityAuditV1Report(
            summary=summary,
            utility_rows=utility_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JOCommercialAerospaceDecisiveEventRegistryExpansionUtilityAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JOCommercialAerospaceDecisiveEventRegistryExpansionUtilityAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134jo_commercial_aerospace_decisive_event_registry_expansion_utility_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
