from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


def _classify_source_tier(source_name: str, source_url: str) -> tuple[str, int]:
    host = urlparse(source_url).netloc.lower()
    source_name = source_name.lower()
    if any(token in host for token in ("cninfo", "sse.com", "szse.cn", "gov.cn")):
        return "T0_official_primary", 5
    if any(token in host for token in ("stcn.com", "yicai.com", "cls.cn", "finance.sina.com.cn", "stockapp.com.cn")):
        return "T2_reliable_media", 4
    if any(token in host for token in ("eastmoney.com", "xueqiu.com", "caifuhao.eastmoney.com")):
        return "T4_social_or_column", 2
    if "research" in source_name or "点评" in source_name:
        return "T3_aggregator_or_secondary", 3
    return "T3_aggregator_or_secondary", 3


def _timestamp_band(status: str, confidence: str) -> str:
    if status == "resolved" and confidence.startswith("matched_expected_date"):
        return "high"
    if status == "resolved":
        return "medium"
    return "low"


def _fetch_band(fetch_status: str) -> str:
    return "high" if fetch_status == "ok" else "low"


@dataclass(slots=True)
class MaterializedAShareQualityFoundationV1:
    summary: dict[str, Any]
    source_quality_rows: list[dict[str, Any]]
    event_quality_rows: list[dict[str, Any]]
    repost_control_rows: list[dict[str, Any]]
    contradiction_backlog_rows: list[dict[str, Any]]


class MaterializeAShareQualityFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.source_master_path = repo_root / "data" / "reference" / "info_center" / "source_master" / "a_share_source_master_v1.csv"
        self.document_registry_path = repo_root / "data" / "reference" / "info_center" / "document_registry" / "a_share_document_registry_v1.csv"
        self.event_registry_path = repo_root / "data" / "reference" / "info_center" / "event_registry" / "a_share_event_registry_v1.csv"
        self.quality_dir = repo_root / "data" / "reference" / "info_center" / "quality_registry"
        self.source_quality_path = self.quality_dir / "a_share_source_quality_registry_v1.csv"
        self.event_quality_path = self.quality_dir / "a_share_event_quality_registry_v1.csv"
        self.repost_control_path = self.quality_dir / "a_share_repost_control_registry_v1.csv"
        self.contradiction_backlog_path = self.quality_dir / "a_share_contradiction_backlog_v1.csv"
        self.manifest_path = self.quality_dir / "a_share_quality_foundation_manifest_v1.json"

    @staticmethod
    def _read_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def materialize(self) -> MaterializedAShareQualityFoundationV1:
        source_rows = self._read_csv(self.source_master_path)
        document_rows = self._read_csv(self.document_registry_path)
        event_rows = self._read_csv(self.event_registry_path)

        source_quality_rows: list[dict[str, Any]] = []
        for row in source_rows:
            source_tier, authority_score = _classify_source_tier(row["source_name"], row["source_url"])
            source_quality_rows.append(
                {
                    "source_id": row["source_id"],
                    "source_tier": source_tier,
                    "authority_score": authority_score,
                    "quality_state": "bootstrap_heuristic",
                    "license_status": row["license_status"],
                }
            )
        source_quality_map = {row["source_id"]: row for row in source_quality_rows}

        document_map = {row["document_id"]: row for row in document_rows}
        event_quality_rows: list[dict[str, Any]] = []
        contradiction_backlog_rows: list[dict[str, Any]] = []
        for row in event_rows:
            document_id = row["claim_id"].replace("_claim_001", "_doc")
            document = document_map.get(document_id, {})
            source_quality = source_quality_map.get(document.get("source_id", ""), {})
            timestamp_quality_band = _timestamp_band(
                row.get("timestamp_resolution_status", ""),
                row.get("timestamp_resolution_confidence", ""),
            )
            fetch_quality_band = _fetch_band(document.get("fetch_status", ""))
            evidence_gate = (
                source_quality.get("source_tier") in {"T0_official_primary", "T2_reliable_media"}
                and timestamp_quality_band in {"high", "medium"}
                and fetch_quality_band == "high"
            )
            event_quality_rows.append(
                {
                    "event_id": row["event_id"],
                    "source_id": document.get("source_id", ""),
                    "timestamp_quality_band": timestamp_quality_band,
                    "fetch_quality_band": fetch_quality_band,
                    "bootstrap_evidence_gate": evidence_gate,
                }
            )
            contradiction_backlog_rows.append(
                {
                    "event_id": row["event_id"],
                    "contradiction_review_status": "unreviewed",
                    "initial_reason": "bootstrap_event_chain_has_not_yet_passed_conflict_review",
                }
            )

        url_counts: dict[str, int] = {}
        source_id_by_url: dict[str, str] = {}
        for row in source_rows:
            url_counts[row["source_url"]] = url_counts.get(row["source_url"], 0) + 1
            source_id_by_url[row["source_url"]] = row["source_id"]
        repost_control_rows = [
            {
                "source_id": source_id_by_url[url],
                "source_url": url,
                "registry_source_count": count,
                "repost_risk_state": "duplicate_registry_reference" if count > 1 else "singleton_reference",
            }
            for url, count in sorted(url_counts.items())
        ]

        self.quality_dir.mkdir(parents=True, exist_ok=True)
        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)

        _write(self.source_quality_path, source_quality_rows)
        _write(self.event_quality_path, event_quality_rows)
        _write(self.repost_control_path, repost_control_rows)
        _write(self.contradiction_backlog_path, contradiction_backlog_rows)

        summary = {
            "materialized_source_quality_count": len(source_quality_rows),
            "materialized_event_quality_count": len(event_quality_rows),
            "materialized_repost_control_count": len(repost_control_rows),
            "contradiction_backlog_count": len(contradiction_backlog_rows),
            "high_authority_source_count": sum(row["authority_score"] >= 4 for row in source_quality_rows),
            "bootstrap_evidence_gate_true_count": sum(bool(row["bootstrap_evidence_gate"]) for row in event_quality_rows),
            "source_quality_path": str(self.source_quality_path.relative_to(self.repo_root)),
            "event_quality_path": str(self.event_quality_path.relative_to(self.repo_root)),
            "repost_control_path": str(self.repost_control_path.relative_to(self.repo_root)),
            "contradiction_backlog_path": str(self.contradiction_backlog_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareQualityFoundationV1(
            summary=summary,
            source_quality_rows=source_quality_rows,
            event_quality_rows=event_quality_rows,
            repost_control_rows=repost_control_rows,
            contradiction_backlog_rows=contradiction_backlog_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareQualityFoundationV1(repo_root).materialize()
    print(result.summary["source_quality_path"])


if __name__ == "__main__":
    main()
