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
class MaterializedAShareSourceActivationFoundationV1:
    summary: dict[str, Any]
    activation_rows: list[dict[str, Any]]
    health_rows: list[dict[str, Any]]
    ingest_rows: list[dict[str, Any]]
    residual_rows: list[dict[str, Any]]


class MaterializeAShareSourceActivationFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.source_master_path = (
            repo_root / "data" / "reference" / "info_center" / "source_master" / "a_share_source_master_v1.csv"
        )
        self.output_ref_dir = repo_root / "data" / "reference" / "info_center" / "automation_registry"
        self.output_ext_dir = repo_root / "data" / "external" / "info_center" / "source_health"
        self.activation_path = self.output_ref_dir / "a_share_source_activation_registry_v1.csv"
        self.ingest_path = self.output_ref_dir / "a_share_ingest_activation_registry_v1.csv"
        self.health_path = self.output_ext_dir / "a_share_source_health_registry_v1.csv"
        self.residual_path = self.output_ref_dir / "a_share_source_activation_residual_backlog_v1.csv"
        self.manifest_path = self.output_ref_dir / "a_share_source_activation_foundation_manifest_v1.json"

    def materialize(self) -> MaterializedAShareSourceActivationFoundationV1:
        source_rows = _read_csv(self.source_master_path)

        local_sources = [
            {
                "source_key": "local_security_master_pack",
                "source_kind": "local_file_feed",
                "activation_state": "active_local_ingest",
                "artifact_or_locator": "data/reference/security_master",
                "target_layer": "identity",
            },
            {
                "source_key": "local_concept_mapping_pack",
                "source_kind": "local_file_feed",
                "activation_state": "active_local_ingest",
                "artifact_or_locator": "data/reference/concept_mapping_daily",
                "target_layer": "taxonomy",
            },
            {
                "source_key": "local_sector_mapping_pack",
                "source_kind": "local_file_feed",
                "activation_state": "active_local_ingest",
                "artifact_or_locator": "data/reference/sector_mapping_daily",
                "target_layer": "taxonomy",
            },
            {
                "source_key": "local_daily_bars_pack",
                "source_kind": "local_file_feed",
                "activation_state": "active_local_ingest",
                "artifact_or_locator": "data/raw/daily_bars",
                "target_layer": "market",
            },
            {
                "source_key": "local_index_daily_bars_pack",
                "source_kind": "local_file_feed",
                "activation_state": "active_local_ingest",
                "artifact_or_locator": "data/raw/index_daily_bars",
                "target_layer": "market",
            },
            {
                "source_key": "local_intraday_zip_pack",
                "source_kind": "local_file_feed",
                "activation_state": "active_local_ingest",
                "artifact_or_locator": "data/raw/intraday_a_share_1min_monthly",
                "target_layer": "market",
            },
            {
                "source_key": "local_catalyst_registry_pack",
                "source_kind": "local_file_feed",
                "activation_state": "active_local_ingest",
                "artifact_or_locator": "data/reference/catalyst_registry",
                "target_layer": "events",
            },
        ]

        activation_rows: list[dict[str, Any]] = []
        for row in local_sources:
            activation_rows.append(row)

        historical_url_count = 0
        placeholder_count = 0
        for row in source_rows:
            url = row["source_url"].strip()
            if url:
                activation_state = "historical_url_catalog_only"
                historical_url_count += 1
            else:
                activation_state = "placeholder_not_activatable"
                placeholder_count += 1
            activation_rows.append(
                {
                    "source_key": row["source_id"],
                    "source_kind": "registry_source_pointer",
                    "activation_state": activation_state,
                    "artifact_or_locator": url,
                    "target_layer": "events",
                }
            )

        health_rows: list[dict[str, Any]] = []
        for row in local_sources:
            path = self.repo_root / Path(row["artifact_or_locator"])
            exists = path.exists()
            file_count = len(list(path.rglob("*"))) if exists and path.is_dir() else (1 if exists else 0)
            health_rows.append(
                {
                    "source_key": row["source_key"],
                    "health_class": "local_path_health",
                    "health_state": "healthy_present" if exists else "missing",
                    "observed_detail": f"file_like_count={file_count}",
                }
            )
        for row in source_rows:
            url = row["source_url"].strip()
            if url:
                health_rows.append(
                    {
                        "source_key": row["source_id"],
                        "health_class": "url_catalog_health",
                        "health_state": "catalogued_unchecked",
                        "observed_detail": url,
                    }
                )
            else:
                health_rows.append(
                    {
                        "source_key": row["source_id"],
                        "health_class": "url_catalog_health",
                        "health_state": "placeholder_missing_locator",
                        "observed_detail": "",
                    }
                )

        ingest_rows = [
            {
                "job_id": "ingest_identity_source_refresh",
                "activation_state": "locally_activatable_now",
                "source_dependency": "local_security_master_pack",
            },
            {
                "job_id": "ingest_event_source_refresh",
                "activation_state": "locally_activatable_now",
                "source_dependency": "local_catalyst_registry_pack",
            },
            {
                "job_id": "ingest_market_coverage_refresh",
                "activation_state": "locally_activatable_now",
                "source_dependency": "local_daily_bars_pack|local_index_daily_bars_pack|local_intraday_zip_pack",
            },
            {
                "job_id": "ingest_network_event_refresh",
                "activation_state": "deferred_no_live_fetch_binding",
                "source_dependency": "source_master_url_catalog",
            },
        ]

        residual_rows = [
            {
                "residual_class": "network_fetch_binding_gap",
                "residual_reason": "url catalog exists but no sanctioned live fetch adapters are bound yet",
            },
            {
                "residual_class": "placeholder_source_gap",
                "residual_reason": "some retained sources are still conceptual placeholders without concrete locators",
            },
        ]

        self.output_ref_dir.mkdir(parents=True, exist_ok=True)
        self.output_ext_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.activation_path, activation_rows)
        _write(self.health_path, health_rows)
        _write(self.ingest_path, ingest_rows)
        _write(self.residual_path, residual_rows)

        summary = {
            "activation_row_count": len(activation_rows),
            "active_local_ingest_count": sum(row["activation_state"] == "active_local_ingest" for row in activation_rows),
            "historical_url_catalog_count": historical_url_count,
            "placeholder_count": placeholder_count,
            "locally_activatable_job_count": sum(row["activation_state"] == "locally_activatable_now" for row in ingest_rows),
            "residual_count": len(residual_rows),
            "activation_path": str(self.activation_path.relative_to(self.repo_root)),
            "health_path": str(self.health_path.relative_to(self.repo_root)),
            "ingest_path": str(self.ingest_path.relative_to(self.repo_root)),
            "residual_path": str(self.residual_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareSourceActivationFoundationV1(
            summary=summary,
            activation_rows=activation_rows,
            health_rows=health_rows,
            ingest_rows=ingest_rows,
            residual_rows=residual_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareSourceActivationFoundationV1(repo_root).materialize()
    print(result.summary["activation_path"])


if __name__ == "__main__":
    main()
