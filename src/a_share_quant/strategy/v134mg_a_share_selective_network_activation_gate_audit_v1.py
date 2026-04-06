from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V134MGAShareSelectiveNetworkActivationGateAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V134MGAShareSelectiveNetworkActivationGateAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.binding_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_fetch_orchestration_binding_v1.csv"
        )
        self.residual_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_fetch_activation_policy_residual_v1.csv"
        )
        self.output_csv = (
            repo_root / "data" / "training" / "a_share_selective_network_activation_gate_status_v1.csv"
        )

    def analyze(self) -> V134MGAShareSelectiveNetworkActivationGateAuditV1Report:
        binding_rows = _read_csv(self.binding_path)
        residual_rows = _read_csv(self.residual_path)

        selective_candidate_host_count = sum(
            row["host_activation_state"] == "selective_candidate_blocked_by_license" for row in binding_rows
        )
        deferred_review_only_count = sum(
            row["host_activation_state"] == "deferred_review_only" for row in binding_rows
        )
        runtime_scheduler_gap_present = any(
            row["residual_class"] == "runtime_scheduler_not_activated" for row in residual_rows
        )
        license_review_gap_present = any(
            row["residual_class"] == "license_review_unresolved" for row in residual_rows
        )

        rows = [
            {
                "gate_id": "license_review_gate",
                "gate_state": "closed",
                "supporting_count": selective_candidate_host_count,
                "gate_reason": "selective candidate hosts exist but all require manual license review before activation",
            },
            {
                "gate_id": "runtime_scheduler_gate",
                "gate_state": "closed",
                "supporting_count": 1 if runtime_scheduler_gap_present else 0,
                "gate_reason": "network adapters are policy-bound but not attached to a live scheduler runtime",
            },
            {
                "gate_id": "review_only_social_gate",
                "gate_state": "deferred_review_only",
                "supporting_count": deferred_review_only_count,
                "gate_reason": "social/column hosts remain review-only and are excluded from activation promotion",
            },
        ]

        self.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with self.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

        summary = {
            "selective_candidate_host_count": selective_candidate_host_count,
            "deferred_review_only_count": deferred_review_only_count,
            "license_review_gap_present": license_review_gap_present,
            "runtime_scheduler_gap_present": runtime_scheduler_gap_present,
            "status_csv": str(self.output_csv.relative_to(self.repo_root)),
            "authoritative_output": "a_share_selective_network_activation_gates_explicit",
        }
        interpretation = [
            "Selective network activation is no longer a vague future task; it is blocked by two explicit gates: license review and runtime scheduler activation.",
            "This separates legitimate T2/T3 article activation candidates from permanently review-only social hosts.",
        ]
        return V134MGAShareSelectiveNetworkActivationGateAuditV1Report(
            summary=summary, rows=rows, interpretation=interpretation
        )


def write_report(
    *, reports_dir: Path, report_name: str, result: V134MGAShareSelectiveNetworkActivationGateAuditV1Report
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V134MGAShareSelectiveNetworkActivationGateAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v134mg_a_share_selective_network_activation_gate_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
