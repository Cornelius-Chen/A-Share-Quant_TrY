from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


@dataclass(slots=True)
class V135CAAShareInternalHotNewsRuntimeSchedulerAuditV1Report:
    summary: dict[str, Any]
    rows: list[dict[str, Any]]
    interpretation: list[str]

    def as_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "rows": self.rows, "interpretation": self.interpretation}


class V135CAAShareInternalHotNewsRuntimeSchedulerAuditV1Analyzer:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.registry_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_runtime_scheduler_registry_v1.csv"
        )
        self.manifest_path = (
            repo_root
            / "data"
            / "reference"
            / "info_center"
            / "automation_registry"
            / "a_share_internal_hot_news_runtime_scheduler_manifest_v1.json"
        )

    def analyze(self) -> V135CAAShareInternalHotNewsRuntimeSchedulerAuditV1Report:
        registry_rows = _read_csv(self.registry_path)
        if not registry_rows:
            raise FileNotFoundError(self.registry_path)
        row = registry_rows[0]
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8")) if self.manifest_path.exists() else {}
        summary = {
            "runtime_state": row["runtime_state"],
            "executed_step_count": int(row["executed_step_count"]),
            "cls_fetch_row_count": int(row["cls_fetch_row_count"]),
            "sina_fetch_row_count": int(row["sina_fetch_row_count"]),
            "top_opportunity_theme": row["top_opportunity_theme"],
            "top_watch_symbol": row["top_watch_symbol"],
            "program_health_state": row["program_health_state"],
            "freshness_state": row["freshness_state"],
            "focus_rotation_readiness_state": row["focus_rotation_readiness_state"],
            "retention_active_queue_count": int(row["retention_active_queue_count"]),
            "retention_expired_cleanup_count": int(row["retention_expired_cleanup_count"]),
            "retention_cap_pruned_file_count": int(row.get("retention_cap_pruned_file_count", 0)),
            "retention_cap_removed_row_count": int(row.get("retention_cap_removed_row_count", 0)),
            "manifest_step_count": len(manifest.get("cycle_steps", [])),
        }
        rows = [
            {"metric": "runtime_state", "value": row["runtime_state"]},
            {"metric": "executed_step_count", "value": row["executed_step_count"]},
            {"metric": "cls_fetch_row_count", "value": row["cls_fetch_row_count"]},
            {"metric": "sina_fetch_row_count", "value": row["sina_fetch_row_count"]},
            {"metric": "top_opportunity_theme", "value": row["top_opportunity_theme"]},
            {"metric": "top_watch_symbol", "value": row["top_watch_symbol"]},
            {"metric": "program_health_state", "value": row["program_health_state"]},
            {"metric": "freshness_state", "value": row["freshness_state"]},
            {"metric": "focus_rotation_readiness_state", "value": row["focus_rotation_readiness_state"]},
            {"metric": "retention_active_queue_count", "value": row["retention_active_queue_count"]},
            {"metric": "retention_expired_cleanup_count", "value": row["retention_expired_cleanup_count"]},
            {
                "metric": "retention_cap_pruned_file_count",
                "value": row.get("retention_cap_pruned_file_count", "0"),
            },
            {
                "metric": "retention_cap_removed_row_count",
                "value": row.get("retention_cap_removed_row_count", "0"),
            },
        ]
        interpretation = [
            "This registry is the single-cycle runtime heartbeat for the internal hot-news stack.",
            "It proves the stack can be externally scheduled without introducing another abstract control layer.",
            "The cycle refreshes fetch, consumer surfaces, focus governance, and the top control packet in one runnable pass.",
            "It also keeps a hot-layer retention queue and records expired hot-copy cleanup so the 5-day TTL is part of the runtime loop.",
            "Runtime artifact retention caps keep history-like files and cleanup logs bounded so continuous running does not drift toward unbounded storage.",
        ]
        return V135CAAShareInternalHotNewsRuntimeSchedulerAuditV1Report(
            summary=summary,
            rows=rows,
            interpretation=interpretation,
        )


def write_report(
    *,
    reports_dir: Path,
    report_name: str,
    result: V135CAAShareInternalHotNewsRuntimeSchedulerAuditV1Report,
) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / f"{report_name}.json"
    output_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    result = V135CAAShareInternalHotNewsRuntimeSchedulerAuditV1Analyzer(repo_root).analyze()
    output_path = write_report(
        reports_dir=repo_root / "reports" / "analysis",
        report_name="v135ca_a_share_internal_hot_news_runtime_scheduler_audit_v1",
        result=result,
    )
    print(output_path)


if __name__ == "__main__":
    main()
