from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class MaterializedAShareAttentionFoundationV1:
    summary: dict[str, Any]
    attention_rows: list[dict[str, Any]]
    backlog_rows: list[dict[str, Any]]


class MaterializeAShareAttentionFoundationV1:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.analysis_dir = repo_root / "reports" / "analysis"
        self.quality_registry_path = (
            repo_root / "data" / "reference" / "info_center" / "quality_registry" / "a_share_source_quality_registry_v1.csv"
        )
        self.source_master_path = (
            repo_root / "data" / "reference" / "info_center" / "source_master" / "a_share_source_master_v1.csv"
        )
        self.output_dir = repo_root / "data" / "reference" / "info_center" / "attention_registry"
        self.attention_registry_path = self.output_dir / "a_share_attention_registry_v1.csv"
        self.attention_backlog_path = self.output_dir / "a_share_attention_backlog_v1.csv"
        self.manifest_path = self.output_dir / "a_share_attention_foundation_manifest_v1.json"

    def _load_json(self, name: str) -> dict[str, Any]:
        return json.loads((self.analysis_dir / name).read_text(encoding="utf-8"))

    @staticmethod
    def _read_csv(path: Path) -> list[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def materialize(self) -> MaterializedAShareAttentionFoundationV1:
        role_audit = self._load_json("v134hy_commercial_aerospace_event_attention_role_candidate_audit_v1.json")
        heat_audit = self._load_json("v134iy_commercial_aerospace_event_attention_heat_proxy_audit_v1.json")
        source_master = self._read_csv(self.source_master_path)
        source_quality = self._read_csv(self.quality_registry_path)

        source_quality_map = {row["source_id"]: row for row in source_quality}
        source_name_to_id = {row["source_name"]: row["source_id"] for row in source_master}

        heat_rows_by_symbol = {row["symbol"]: row for row in heat_audit["heat_proxy_rows"]}
        attention_rows: list[dict[str, Any]] = []
        backlog_rows: list[dict[str, Any]] = []

        for row in role_audit["candidate_rows"]:
            heat_row = heat_rows_by_symbol.get(row["symbol"], {})
            source_backing = row.get("source_backing", "")
            source_id = ""
            if "ca_source_007" in source_backing:
                # direct known mapping
                for name, sid in source_name_to_id.items():
                    if "航天发展" in row["display_name"] and "新浪财经-军工股全线走强" in name:
                        source_id = sid
                        break
            confidence_state = "hard_role" if row["candidate_status"] == "hard_retained" else "soft_role_candidate"
            attention_rows.append(
                {
                    "symbol": row["symbol"],
                    "display_name": row["display_name"],
                    "attention_role": row["candidate_role"],
                    "heat_proxy_class": heat_row.get("heat_proxy_class", ""),
                    "candidate_status": row["candidate_status"],
                    "confidence_state": confidence_state,
                    "source_backing": source_backing,
                    "linked_source_id": source_id,
                    "quality_guardrail": (
                        source_quality_map.get(source_id, {}).get("source_tier", "unrated_bootstrap")
                        if source_id
                        else "needs_manual_link"
                    ),
                }
            )
            if row["candidate_status"] != "hard_retained":
                backlog_rows.append(
                    {
                        "symbol": row["symbol"],
                        "display_name": row["display_name"],
                        "backlog_reason": "soft_attention_candidate_requires_more_evidence_before_hard_anchor_or_decoy_promotion",
                        "current_role": row["candidate_role"],
                    }
                )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        with self.attention_registry_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(attention_rows[0].keys()))
            writer.writeheader()
            writer.writerows(attention_rows)
        with self.attention_backlog_path.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(backlog_rows[0].keys()))
            writer.writeheader()
            writer.writerows(backlog_rows)

        summary = {
            "attention_registry_count": len(attention_rows),
            "hard_attention_role_count": sum(row["candidate_status"] == "hard_retained" for row in attention_rows),
            "soft_attention_candidate_count": sum(row["candidate_status"] != "hard_retained" for row in attention_rows),
            "backlog_count": len(backlog_rows),
            "attention_registry_path": str(self.attention_registry_path.relative_to(self.repo_root)),
            "attention_backlog_path": str(self.attention_backlog_path.relative_to(self.repo_root)),
        }
        self.manifest_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return MaterializedAShareAttentionFoundationV1(
            summary=summary,
            attention_rows=attention_rows,
            backlog_rows=backlog_rows,
        )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[5]
    result = MaterializeAShareAttentionFoundationV1(repo_root).materialize()
    print(result.summary["attention_registry_path"])


if __name__ == "__main__":
    main()
