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
class MaterializedAShareNetworkFetchAdapterFoundationV1:
    summary: dict[str, Any]
    adapter_rows: list[dict[str, Any]]
    host_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareNetworkFetchAdapterFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.source_master_path = (
            repo_root / "data" / "reference" / "info_center" / "source_master" / "a_share_source_master_v1.csv"
        )
        self.source_quality_path = (
            repo_root / "data" / "reference" / "info_center" / "quality_registry" / "a_share_source_quality_registry_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "automation_registry"
        self.adapter_path = self.output_dir / "a_share_network_fetch_adapter_registry_v1.csv"
        self.host_path = self.output_dir / "a_share_network_fetch_host_registry_v1.csv"
        self.residual_path = self.output_dir / "a_share_network_fetch_adapter_residual_backlog_v1.csv"
        self.manifest_path = self.output_dir / "a_share_network_fetch_adapter_foundation_manifest_v1.json"

    def materialize(self) -> MaterializedAShareNetworkFetchAdapterFoundationV1:
        source_rows = _read_csv(self.source_master_path)
        quality_rows = _read_csv(self.source_quality_path)
        quality_by_id = {row["source_id"]: row for row in quality_rows}

        host_rows: list[dict[str, Any]] = []
        for row in source_rows:
            url = row["source_url"].strip()
            if not url:
                continue
            host = url.split("/")[2] if "://" in url else ""
            tier = quality_by_id.get(row["source_id"], {}).get("source_tier", "unknown")
            if tier == "T2_reliable_media":
                adapter_family = "html_article_fetch"
                adapter_state = "adapter_stub_ready"
            elif tier == "T3_aggregator_or_secondary":
                adapter_family = "html_article_fetch_with_review_bias"
                adapter_state = "adapter_stub_ready"
            elif tier == "T4_social_or_column":
                adapter_family = "social_column_fetch_with_noise_guard"
                adapter_state = "adapter_stub_ready"
            else:
                adapter_family = "unclassified_fetch"
                adapter_state = "adapter_stub_backlog"
            host_rows.append(
                {
                    "source_id": row["source_id"],
                    "host": host,
                    "source_tier": tier,
                    "adapter_family": adapter_family,
                    "adapter_state": adapter_state,
                }
            )

        adapter_rows = [
            {
                "adapter_id": "network_html_article_fetch",
                "adapter_scope": "T2_T3_articles",
                "adapter_state": "contract_defined_not_activated",
            },
            {
                "adapter_id": "network_social_column_fetch",
                "adapter_scope": "T4_social_or_column",
                "adapter_state": "contract_defined_not_activated",
            },
            {
                "adapter_id": "network_official_source_fetch",
                "adapter_scope": "future_T0_T1_official_sources",
                "adapter_state": "contract_defined_not_activated",
            },
        ]

        residual_rows = [
            {
                "residual_class": "scheduler_binding_gap",
                "residual_reason": "network adapters are defined but not yet bound to orchestration and retry loops",
            },
            {
                "residual_class": "license_and_terms_gap",
                "residual_reason": "historical URL catalog still carries unknown license status for most sources",
            },
            {
                "residual_class": "official_source_coverage_gap",
                "residual_reason": "current retained source catalog is dominated by media and secondary articles rather than official primary APIs",
            },
        ]

        self.output_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.adapter_path, adapter_rows)
        _write(self.host_path, host_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "adapter_count": len(adapter_rows),
            "host_binding_count": len(host_rows),
            "stub_ready_host_count": sum(row["adapter_state"] == "adapter_stub_ready" for row in host_rows),
            "residual_count": len(residual_rows),
            "adapter_path": str(self.adapter_path.relative_to(self.repo_root)),
            "host_path": str(self.host_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareNetworkFetchAdapterFoundationV1(
            summary=summary, adapter_rows=adapter_rows, host_rows=host_rows, residual_rows=residual_rows
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareNetworkFetchAdapterFoundationV1(repo_root).materialize()
    print(result.summary["adapter_path"])


if __name__ == "__main__":
    main()
