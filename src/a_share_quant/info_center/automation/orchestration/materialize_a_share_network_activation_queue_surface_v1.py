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
class MaterializedAShareNetworkActivationQueueSurfaceV1:
    summary: dict[str, Any]
    allowlist_rows: list[dict[str, Any]]
    runtime_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareNetworkActivationQueueSurfaceV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.license_review_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_license_review_registry_v1.csv"
        )
        self.scheduler_runtime_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_scheduler_runtime_registry_v1.csv"
        )
        self.output_dir = repo_root / "data" / "temp" / "info_center" / "review_queue"
        self.allowlist_queue_path = self.output_dir / "a_share_network_allowlist_decision_queue_v1.csv"
        self.runtime_queue_path = self.output_dir / "a_share_network_runtime_deployment_queue_v1.csv"
        self.residual_path = self.output_dir / "a_share_network_activation_queue_residual_v1.csv"
        self.manifest_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_network_activation_queue_surface_manifest_v1.json"
        )

    def materialize(self) -> MaterializedAShareNetworkActivationQueueSurfaceV1:
        license_rows = _read_csv(self.license_review_path)
        runtime_rows = _read_csv(self.scheduler_runtime_path)

        allowlist_rows = [
            {
                "source_id": row["source_id"],
                "host": row["host"],
                "source_tier": row["source_tier"],
                "queue_state": "awaiting_allowlist_decision",
                "decision_scope": row["activation_eligibility"],
            }
            for row in license_rows
            if row["license_review_state"] == "manual_review_pending"
        ]
        runtime_queue_rows = [
            {
                "adapter_id": row["adapter_id"],
                "flow_id": row["flow_id"],
                "queue_state": "awaiting_runtime_deployment",
                "deployment_scope": row["activation_scope"],
            }
            for row in runtime_rows
            if row["runtime_binding_state"] == "scheduler_stub_not_activated"
        ]
        residual_rows = [
            {
                "residual_class": "allowlist_decisions_missing",
                "residual_reason": "all selective candidates remain queued and none are approved yet",
            },
            {
                "residual_class": "runtime_deployment_missing",
                "residual_reason": "all adapter runtimes remain queued and none are deployed yet",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.allowlist_queue_path, allowlist_rows)
        _write(self.runtime_queue_path, runtime_queue_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "allowlist_queue_count": len(allowlist_rows),
            "runtime_queue_count": len(runtime_queue_rows),
            "allowlist_queue_path": str(self.allowlist_queue_path.relative_to(self.repo_root)),
            "runtime_queue_path": str(self.runtime_queue_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareNetworkActivationQueueSurfaceV1(
            summary=summary,
            allowlist_rows=allowlist_rows,
            runtime_rows=runtime_queue_rows,
            residual_rows=residual_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareNetworkActivationQueueSurfaceV1(repo_root).materialize()
    print(result.summary["allowlist_queue_path"])


if __name__ == "__main__":
    main()
