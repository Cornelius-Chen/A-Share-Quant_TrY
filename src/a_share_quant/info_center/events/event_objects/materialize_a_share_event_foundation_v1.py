from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MaterializedAShareEventFoundationV1:
    summary: dict[str, Any]
    source_rows: list[dict[str, Any]]
    document_rows: list[dict[str, Any]]
    claim_rows: list[dict[str, Any]]
    event_rows: list[dict[str, Any]]
    evidence_rows: list[dict[str, Any]]


class MaterializeAShareEventFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.input_dir = repo_root / "data" / "reference" / "catalyst_registry"
        self.output_root = repo_root / "data" / "reference" / "info_center"
        self.source_master_path = self.output_root / "source_master" / "a_share_source_master_v1.csv"
        self.document_registry_path = self.output_root / "document_registry" / "a_share_document_registry_v1.csv"
        self.claim_registry_path = self.output_root / "claim_registry" / "a_share_claim_registry_v1.csv"
        self.event_registry_path = self.output_root / "event_registry" / "a_share_event_registry_v1.csv"
        self.evidence_registry_path = self.output_root / "evidence_span_registry" / "a_share_evidence_span_registry_v1.csv"
        self.manifest_path = self.output_root / "event_registry" / "a_share_event_foundation_manifest_v1.json"

    def _load_rows(self) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        for path in sorted(self.input_dir.glob("*.csv")):
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    rows.append({**row, "source_file": path.name})
        return rows

    def materialize(self) -> MaterializedAShareEventFoundationV1:
        input_rows = self._load_rows()

        source_key_to_id: dict[tuple[str, str], str] = {}
        source_rows: list[dict[str, Any]] = []
        document_rows: list[dict[str, Any]] = []
        claim_rows: list[dict[str, Any]] = []
        event_rows: list[dict[str, Any]] = []
        evidence_rows: list[dict[str, Any]] = []

        for row in input_rows:
            source_key = (row.get("source_name", ""), row.get("source_url", ""))
            if source_key not in source_key_to_id:
                source_id = f"src_{len(source_key_to_id) + 1:04d}"
                source_key_to_id[source_key] = source_id
                source_rows.append(
                    {
                        "source_id": source_id,
                        "source_name": row.get("source_name", ""),
                        "source_url": row.get("source_url", ""),
                        "source_tier": "unrated_bootstrap",
                        "availability_mode": "historical_registry_bootstrap",
                        "license_status": "unknown",
                    }
                )
            source_id = source_key_to_id[source_key]
            registry_id = row.get("registry_id", "")
            document_id = f"{registry_id}_doc"
            claim_id = f"{registry_id}_claim_001"
            event_id = f"{registry_id}_event"
            evidence_span_id = f"{registry_id}_evidence_001"
            notes = row.get("notes", "")
            decisive_reason = row.get("decisive_reason", "")
            claim_text = " | ".join(part for part in (notes, decisive_reason) if part)

            document_rows.append(
                {
                    "document_id": document_id,
                    "source_id": source_id,
                    "registry_id": registry_id,
                    "source_file": row.get("source_file", ""),
                    "record_type": row.get("record_type", ""),
                    "public_ts": row.get("public_release_time", ""),
                    "system_visible_ts": row.get("system_visible_time", ""),
                    "fetch_status": row.get("fetch_status", ""),
                }
            )
            claim_rows.append(
                {
                    "claim_id": claim_id,
                    "document_id": document_id,
                    "claim_text": claim_text,
                    "claim_scope": row.get("event_scope", ""),
                    "claim_confidence": row.get("timestamp_resolution_confidence", ""),
                }
            )
            event_rows.append(
                {
                    "event_id": event_id,
                    "claim_id": claim_id,
                    "registry_id": registry_id,
                    "layer": row.get("layer", ""),
                    "event_scope": row.get("event_scope", ""),
                    "event_occurred_ts": row.get("event_occurred_time", ""),
                    "public_ts": row.get("public_release_time", ""),
                    "system_visible_ts": row.get("system_visible_time", ""),
                    "timezone": row.get("timezone", ""),
                    "timestamp_resolution_status": row.get("timestamp_resolution_status", ""),
                    "timestamp_resolution_confidence": row.get("timestamp_resolution_confidence", ""),
                    "decisive_retained": row.get("decisive_retained", ""),
                }
            )
            evidence_rows.append(
                {
                    "evidence_span_id": evidence_span_id,
                    "document_id": document_id,
                    "claim_id": claim_id,
                    "evidence_type": "registry_notes",
                    "evidence_text": notes,
                }
            )

        for path in (
            self.source_master_path.parent,
            self.document_registry_path.parent,
            self.claim_registry_path.parent,
            self.event_registry_path.parent,
            self.evidence_registry_path.parent,
        ):
            path.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.source_master_path, source_rows)
        _write(self.document_registry_path, document_rows)
        _write(self.claim_registry_path, claim_rows)
        _write(self.event_registry_path, event_rows)
        _write(self.evidence_registry_path, evidence_rows)

        summary = {
            "input_registry_row_count": len(input_rows),
            "materialized_source_count": len(source_rows),
            "materialized_document_count": len(document_rows),
            "materialized_claim_count": len(claim_rows),
            "materialized_event_count": len(event_rows),
            "materialized_evidence_count": len(evidence_rows),
            "source_master_path": str(self.source_master_path.relative_to(self.repo_root)),
            "document_registry_path": str(self.document_registry_path.relative_to(self.repo_root)),
            "claim_registry_path": str(self.claim_registry_path.relative_to(self.repo_root)),
            "event_registry_path": str(self.event_registry_path.relative_to(self.repo_root)),
            "evidence_registry_path": str(self.evidence_registry_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareEventFoundationV1(
            summary=summary,
            source_rows=source_rows,
            document_rows=document_rows,
            claim_rows=claim_rows,
            event_rows=event_rows,
            evidence_rows=evidence_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    result = MaterializeAShareEventFoundationV1(repo_root).materialize()
    print(result.summary["event_registry_path"])


if __name__ == "__main__":
    main()
