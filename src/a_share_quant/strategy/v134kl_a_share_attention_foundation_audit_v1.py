from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from a_share_quant.info_center.attention.signals.materialize_a_share_attention_foundation_v1 import (
    MaterializeAShareAttentionFoundationV1,
)


@dataclass(slots=True)
class V134KLAShareAttentionFoundationAuditV1Report:
    summary: dict[str, Any]
    attention_rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "attention_rows": self.attention_rows,
            "interpretation": self.interpretation,
        }


class V134KLAShareAttentionFoundationAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.output_csv = repo_root / "data" / "training" / "a_share_attention_foundation_status_v1.csv"

    def analyze(self) -> V134KLAShareAttentionFoundationAuditV1Report:
        materialized = MaterializeAShareAttentionFoundationV1(self.repo_root).materialize()
        summary = materialized.summary
        attention_rows = [
            {
                "attention_component": "attention_registry",
                "component_state": "materialized_bootstrap",
                "artifact_path": summary["attention_registry_path"],
                "coverage_note": f"attention_registry_count = {summary['attention_registry_count']}",
            },
            {
                "attention_component": "hard_attention_roles",
                "component_state": "singleton_hard_case_present",
                "artifact_path": summary["attention_registry_path"],
                "coverage_note": f"hard_attention_role_count = {summary['hard_attention_role_count']}",
            },
            {
                "attention_component": "soft_attention_candidates",
                "component_state": "materialized_backlog_driven",
                "artifact_path": summary["attention_backlog_path"],
                "coverage_note": f"soft_attention_candidate_count = {summary['soft_attention_candidate_count']}",
            },
        ]
        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(attention_rows[0].keys()))
            writer.writeheader()
            writer.writerows(attention_rows)

        report_summary = {
            "acceptance_posture": "build_v134kl_a_share_attention_foundation_audit_v1",
            "attention_registry_count": summary["attention_registry_count"],
            "hard_attention_role_count": summary["hard_attention_role_count"],
            "soft_attention_candidate_count": summary["soft_attention_candidate_count"],
            "attention_status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_attention_foundation_ready_for_direction_triage",
        }
        interpretation = [
            "V1.34KL completes the first attention workstream pass by converting existing anchor/decoy and heat-proxy research into a central bootstrap attention registry.",
            "The registry is intentionally asymmetric: one hard retained case and multiple soft candidates, with backlog status preserved instead of overpromotion.",
        ]
        return V134KLAShareAttentionFoundationAuditV1Report(
            summary=report_summary,
            attention_rows=attention_rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V134KLAShareAttentionFoundationAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134KLAShareAttentionFoundationAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134kl_a_share_attention_foundation_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
