from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class V134JUCommercialAerospaceCarrierFollowSearchExpansionAuditV1Report:
    summary: dict[str, Any]
    expansion_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "expansion_rows": self.expansion_rows,
            "interpretation": self.interpretation,
        }


class V134JUCommercialAerospaceCarrierFollowSearchExpansionAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "catalyst_registry"
            / "commercial_aerospace_decisive_event_registry_v1.csv"
        )
        self.followthrough_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134ii_commercial_aerospace_symbol_followthrough_supervision_audit_v1.json"
        )
        self.source_hardness_path = (
            repo_root
            / "reports"
            / "analysis"
            / "v134ja_commercial_aerospace_event_attention_source_hardness_audit_v1.json"
        )
        self.output_csv = (
            repo_root
            / "data"
            / "training"
            / "commercial_aerospace_carrier_follow_search_expansion_v1.csv"
        )

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _load_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def analyze(self) -> V134JUCommercialAerospaceCarrierFollowSearchExpansionAuditV1Report:
        registry_rows = self._load_csv(self.registry_path)
        followthrough = self._load_json(self.followthrough_path)
        source_hardness = self._load_json(self.source_hardness_path)

        supply_chain_rows = [
            row
            for row in registry_rows
            if row["decisive_retained"] == "True" and row["decisive_reason"] == "supply_chain_validation"
        ]
        source_hardness_by_id = {
            row["event_registry_id"]: row for row in source_hardness["source_rows"] if row.get("event_registry_id")
        }
        followthrough_by_symbol = {row["symbol"]: row for row in followthrough["followthrough_rows"]}

        expansion_rows: list[dict[str, Any]] = []
        linked_local_count = 0
        outside_named_watch_count = 0
        persistent_link_count = 0
        moderate_link_count = 0

        for row in supply_chain_rows:
            if row["registry_id"] == "ca_source_010":
                symbol = "603601"
                symbol_label = followthrough_by_symbol[symbol]["followthrough_label"]
                linked_local_count += 1
                persistent_link_count += 1
                expansion_rows.append(
                    {
                        "registry_id": row["registry_id"],
                        "linked_symbol": symbol,
                        "branch_role": "linked_carrier_case",
                        "followthrough_label": symbol_label,
                        "source_hardness": source_hardness_by_id[row["registry_id"]]["source_hardness"],
                        "expansion_reading": "same_plane_carrier_reinforcement_without_true_selection_promotion",
                    }
                )
            elif row["registry_id"] == "ca_source_011":
                symbol = "301306"
                symbol_label = followthrough_by_symbol[symbol]["followthrough_label"]
                linked_local_count += 1
                moderate_link_count += 1
                expansion_rows.append(
                    {
                        "registry_id": row["registry_id"],
                        "linked_symbol": symbol,
                        "branch_role": "linked_follow_case",
                        "followthrough_label": symbol_label,
                        "source_hardness": source_hardness_by_id[row["registry_id"]]["source_hardness"],
                        "expansion_reading": "same_plane_follow_reinforcement_without_anchor_upgrade",
                    }
                )
            else:
                outside_named_watch_count += 1
                expansion_rows.append(
                    {
                        "registry_id": row["registry_id"],
                        "linked_symbol": "outside_named_candidate_watch",
                        "branch_role": "outside_named_supply_chain_watch",
                        "followthrough_label": "unobserved_in_current_local_surface",
                        "source_hardness": "retained_continuation_support_source",
                        "expansion_reading": "same_plane_registry_support_exists_but_local_symbol_surface_not_materialized",
                    }
                )

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(expansion_rows[0].keys()))
            writer.writeheader()
            writer.writerows(expansion_rows)

        summary = {
            "acceptance_posture": "freeze_v134ju_commercial_aerospace_carrier_follow_search_expansion_audit_v1",
            "retained_supply_chain_source_count": len(supply_chain_rows),
            "linked_local_case_count": linked_local_count,
            "persistent_link_count": persistent_link_count,
            "moderate_link_count": moderate_link_count,
            "outside_named_watch_count": outside_named_watch_count,
            "branch_formalized": True,
            "branch_promotive": False,
            "expansion_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "commercial_aerospace_carrier_follow_search_expansion_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34JU formalizes the carrier-follow branch using retained supply-chain validation sources.",
            "The branch adds real same-plane reinforcement for 603601 and 301306, while also surfacing one outside-named supply-chain watch, but it still does not justify true-selection promotion.",
        ]
        return V134JUCommercialAerospaceCarrierFollowSearchExpansionAuditV1Report(
            summary=summary,
            expansion_rows=expansion_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134JUCommercialAerospaceCarrierFollowSearchExpansionAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134JUCommercialAerospaceCarrierFollowSearchExpansionAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134ju_commercial_aerospace_carrier_follow_search_expansion_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
