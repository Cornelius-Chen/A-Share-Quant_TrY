from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.identity.pipelines.materialize_a_share_identity_foundation_v1 import (
    MaterializeAShareIdentityFoundationV1,
)


@dataclass(slots=True)
class V134KCAShareIdentityFoundationAuditV1Report:
    summary: dict[str, Any]
    identity_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "identity_rows": self.identity_rows,
            "interpretation": self.interpretation,
        }


class V134KCAShareIdentityFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_identity_foundation_status_v1.csv"

    def analyze(self) -> V134KCAShareIdentityFoundationAuditV1Report:
        materialized = MaterializeAShareIdentityFoundationV1(self.repo_root).materialize()
        manifest = materialized.summary
        identity_rows = [
            {
                "identity_component": "security_master",
                "component_state": "materialized_foundation",
                "artifact_path": manifest["security_master_path"],
                "coverage_note": f"materialized_symbol_count = {manifest['materialized_symbol_count']}",
            },
            {
                "identity_component": "entity_alias_map",
                "component_state": "materialized_foundation",
                "artifact_path": manifest["alias_map_path"],
                "coverage_note": f"materialized_alias_count = {manifest['materialized_alias_count']}",
            },
            {
                "identity_component": "name_to_symbol_resolution",
                "component_state": "seed_ready_from_alias_map",
                "artifact_path": manifest["alias_map_path"],
                "coverage_note": f"multi_source_symbol_count = {manifest['multi_source_symbol_count']}",
            },
            {
                "identity_component": "identity_source_priority_manifest",
                "component_state": "explicit_priority_rules_present",
                "artifact_path": "data/reference/info_center/identity/a_share_identity_foundation_manifest_v1.json",
                "coverage_note": f"input_source_file_count = {manifest['input_source_file_count']}",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(identity_rows[0].keys()))
            writer.writeheader()
            writer.writerows(identity_rows)

        summary = {
            "acceptance_posture": "build_v134kc_a_share_identity_foundation_audit_v1",
            "materialized_symbol_count": manifest["materialized_symbol_count"],
            "materialized_alias_count": manifest["materialized_alias_count"],
            "multi_source_symbol_count": manifest["multi_source_symbol_count"],
            "input_source_file_count": manifest["input_source_file_count"],
            "identity_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_identity_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KC completes the first full identity workstream pass: a materialized security master, alias map, and explicit source-priority manifest.",
            "Identity is now beyond scaffold-only status and can serve as the first reusable foundation for taxonomy, events, and later point-in-time ledgers.",
        ]
        return V134KCAShareIdentityFoundationAuditV1Report(
            summary=summary,
            identity_rows=identity_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KCAShareIdentityFoundationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KCAShareIdentityFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kc_a_share_identity_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
