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
class MaterializedAShareNetworkActivationOperationalRegistryV1:
    summary: dict[str, Any]
    license_rows: list[dict[str, Any]]
    scheduler_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareNetworkActivationOperationalRegistryV1:
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
        self.policy_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_fetch_activation_policy_v1.csv"
        )
        self.source_master_path = (
            repo_root / "data" / "reference" / "info_center" / "source_master" / "a_share_source_master_v1.csv"
        )
        self.quality_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "quality_registry"
            / "a_share_source_quality_registry_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "automation_registry"
        self.license_path = self.output_dir / "a_share_network_license_review_registry_v1.csv"
        self.scheduler_path = self.output_dir / "a_share_network_scheduler_runtime_registry_v1.csv"
        self.residual_path = self.output_dir / "a_share_network_activation_operational_residual_v1.csv"
        self.manifest_path = self.output_dir / "a_share_network_activation_operational_manifest_v1.json"

    def materialize(self) -> MaterializedAShareNetworkActivationOperationalRegistryV1:
        binding_rows = _read_csv(self.binding_path)
        policy_rows = _read_csv(self.policy_path)
        source_rows = _read_csv(self.source_master_path)
        quality_rows = _read_csv(self.quality_path)
        source_by_id = {row["source_id"]: row for row in source_rows}
        quality_by_id = {row["source_id"]: row for row in quality_rows}

        license_rows: list[dict[str, Any]] = []
        review_only_excluded_count = 0
        for row in binding_rows:
            source_id = row["source_id"]
            source = source_by_id[source_id]
            quality = quality_by_id[source_id]
            if row["activation_gate"] == "license_review_required":
                review_state = "manual_review_pending"
                activation_eligibility = "selective_candidate_after_allowlist"
            else:
                review_state = "not_applicable_review_only"
                activation_eligibility = "excluded_from_activation_promotion"
                review_only_excluded_count += 1
            license_rows.append(
                {
                    "source_id": source_id,
                    "source_name": source["source_name"],
                    "host": row["host"],
                    "source_tier": quality["source_tier"],
                    "license_status": source["license_status"],
                    "license_review_state": review_state,
                    "activation_eligibility": activation_eligibility,
                }
            )

        scheduler_rows: list[dict[str, Any]] = []
        for row in policy_rows:
            scheduler_rows.append(
                {
                    "adapter_id": row["adapter_id"],
                    "flow_id": row["flow_id"],
                    "retry_policy_id": row["retry_policy_id"],
                    "runtime_binding_state": "scheduler_stub_not_activated",
                    "activation_scope": row["activation_posture"],
                }
            )

        residual_rows = [
            {
                "residual_class": "allowlist_not_reviewed",
                "residual_reason": "selective candidate hosts are inventoried but no explicit allowlist decisions have been made yet",
            },
            {
                "residual_class": "scheduler_runtime_not_deployed",
                "residual_reason": "runtime bindings remain stubbed and are not attached to a recurring scheduler process",
            },
            {
                "residual_class": "review_only_hosts_nonpromotive",
                "residual_reason": "social and column sources stay excluded from activation promotion even after operational registries exist",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.license_path, license_rows)
        _write(self.scheduler_path, scheduler_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "license_review_row_count": len(license_rows),
            "scheduler_runtime_row_count": len(scheduler_rows),
            "review_only_excluded_count": review_only_excluded_count,
            "license_path": str(self.license_path.relative_to(self.repo_root)),
            "scheduler_path": str(self.scheduler_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareNetworkActivationOperationalRegistryV1(
            summary=summary,
            license_rows=license_rows,
            scheduler_rows=scheduler_rows,
            residual_rows=residual_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareNetworkActivationOperationalRegistryV1(repo_root).materialize()
    print(result.summary["license_path"])


if __name__ == "__main__":
    main()
