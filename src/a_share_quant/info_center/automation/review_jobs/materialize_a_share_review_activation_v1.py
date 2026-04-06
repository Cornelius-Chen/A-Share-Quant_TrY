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
class MaterializedAShareReviewActivationV1:
    summary: dict[str, Any]
    registry_rows: list[dict[str, Any]]
    low_conf_rows: list[dict[str, Any]]
    contradiction_rows: list[dict[str, Any]]
    attention_rows: list[dict[str, Any]]


class MaterializeAShareReviewActivationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.event_quality_path = (
            repo_root / "data" / "reference" / "info_center" / "quality_registry" / "a_share_event_quality_registry_v1.csv"
        )
        self.contradiction_queue_path = (
            repo_root / "data" / "reference" / "info_center" / "quality_registry" / "a_share_contradiction_review_queue_v1.csv"
        )
        self.attention_path = (
            repo_root / "data" / "reference" / "info_center" / "attention_registry" / "a_share_attention_registry_v1.csv"
        )
        self.ref_dir = repo_root / "data" / "reference" / "info_center" / "automation_registry"
        self.temp_dir = repo_root / "data" / "temp" / "info_center" / "review_queue"
        self.registry_path = self.ref_dir / "a_share_review_activation_registry_v1.csv"
        self.low_conf_path = self.temp_dir / "a_share_low_confidence_event_queue_v1.csv"
        self.contradiction_path = self.temp_dir / "a_share_contradiction_queue_v1.csv"
        self.attention_queue_path = self.temp_dir / "a_share_attention_soft_candidate_queue_v1.csv"
        self.manifest_path = self.ref_dir / "a_share_review_activation_manifest_v1.json"

    def materialize(self) -> MaterializedAShareReviewActivationV1:
        event_quality_rows = _read_csv(self.event_quality_path)
        contradiction_rows = _read_csv(self.contradiction_queue_path)
        attention_rows = _read_csv(self.attention_path)

        low_conf_rows = [
            {
                "review_target": row["event_id"],
                "queue_class": "low_confidence_event",
                "priority": (
                    "high"
                    if row["timestamp_quality_band"] == "low" or row["fetch_quality_band"] == "low"
                    else "normal"
                ),
                "timestamp_quality_band": row["timestamp_quality_band"],
                "fetch_quality_band": row["fetch_quality_band"],
                "bootstrap_evidence_gate": row["bootstrap_evidence_gate"],
            }
            for row in event_quality_rows
            if str(row["bootstrap_evidence_gate"]) == "False"
        ]
        contradiction_queue_rows = [
            {
                "review_target": row["review_target"],
                "queue_class": row["review_class"],
                "priority": "high" if row["review_class"] == "semantic_divergence" else "normal",
                "review_reason": row["review_reason"],
            }
            for row in contradiction_rows
            if row["review_target"]
        ]
        attention_queue_rows = [
            {
                "review_target": row["symbol"],
                "queue_class": "attention_soft_candidate",
                "priority": "normal",
                "attention_role": row["attention_role"],
                "heat_proxy_class": row["heat_proxy_class"],
                "source_backing": row["source_backing"],
            }
            for row in attention_rows
            if row["candidate_status"] == "soft_candidate"
        ]

        registry_rows = [
            {
                "queue_id": "low_confidence_event_queue",
                "queue_state": "active_bootstrap",
                "artifact_path": str(self.low_conf_path.relative_to(self.repo_root)),
                "queue_size": len(low_conf_rows),
            },
            {
                "queue_id": "contradiction_queue",
                "queue_state": "active_bootstrap",
                "artifact_path": str(self.contradiction_path.relative_to(self.repo_root)),
                "queue_size": len(contradiction_queue_rows),
            },
            {
                "queue_id": "attention_soft_candidate_queue",
                "queue_state": "active_bootstrap",
                "artifact_path": str(self.attention_queue_path.relative_to(self.repo_root)),
                "queue_size": len(attention_queue_rows),
            },
        ]

        self.ref_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        def _write(path: Path, rows: list[dict[str, Any]]) -> None:
            safe_rows = rows or [{"placeholder": ""}]
            with path.open("w", encoding="utf-8-sig", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(safe_rows[0].keys()))
                writer.writeheader()
                writer.writerows(safe_rows)

        _write(self.registry_path, registry_rows)
        _write(self.low_conf_path, low_conf_rows)
        _write(self.contradiction_path, contradiction_queue_rows)
        _write(self.attention_queue_path, attention_queue_rows)

        summary = {
            "review_registry_count": len(registry_rows),
            "low_confidence_queue_count": len(low_conf_rows),
            "contradiction_queue_count": len(contradiction_queue_rows),
            "attention_soft_queue_count": len(attention_queue_rows),
            "registry_path": str(self.registry_path.relative_to(self.repo_root)),
            "low_conf_path": str(self.low_conf_path.relative_to(self.repo_root)),
            "contradiction_path": str(self.contradiction_path.relative_to(self.repo_root)),
            "attention_queue_path": str(self.attention_queue_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareReviewActivationV1(
            summary=summary,
            registry_rows=registry_rows,
            low_conf_rows=low_conf_rows,
            contradiction_rows=contradiction_queue_rows,
            attention_rows=attention_queue_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    result = MaterializeAShareReviewActivationV1(repo_root).materialize()
    print(result.summary["registry_path"])


if __name__ == "__main__":
    main()
